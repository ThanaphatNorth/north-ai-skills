"""Failure audit of the local board: a bad input or an OS failure is one line on stderr and an exit code.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import contextlib
import errno
import io
import os
import shutil
import stat
import subprocess
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_tracker import SCRIPTS, TRACKER, card, local_project, read, run  # noqa: E402

sys.path.insert(0, SCRIPTS)
import local_board  # noqa: E402

LOCAL_BOARD = os.path.join(SCRIPTS, "local_board.py")
AS_ROOT = hasattr(os, "geteuid") and os.geteuid() == 0  # root reads what file modes forbid everyone else
NOT_UTF8 = b"---\ntitle: \xff\xfe\nstatus: todo\n---\n\n## Comments\n"


class BoardCase(unittest.TestCase):
    """A project with two cards. `t` runs tracker.sh in it; `refused` checks the one-line failure contract."""

    def setUp(self):
        self.root, self.dl, self.env = local_project({
            "TASK-1": card("first", extra="severity: Level 4\n"), "TASK-2": card("second", rank="5")})
        self.board = os.path.join(self.dl, "board")
        self.addCleanup(shutil.rmtree, self.root, True)

    def t(self, *args):
        return run(list(args), self.root, self.env)

    def card_path(self, key):
        return os.path.join(self.board, key + ".md")

    def file(self, name, data):
        """Write `data` (text or bytes) at `name` under the project root; returns the path."""
        path = os.path.join(self.root, name)
        with open(path, "wb") as fh:
            fh.write(data if isinstance(data, bytes) else data.encode("utf-8"))
        return path

    def mode(self, path, bits):
        """chmod now, and back to a mode that lets the temp folder be removed afterwards."""
        self.addCleanup(os.chmod, path, stat.S_IMODE(os.stat(path).st_mode))
        os.chmod(path, bits)

    def refused(self, r, says="", code=1):
        self.assertEqual(r.returncode, code, r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(len([line for line in r.stderr.splitlines() if line.strip()]), 1, r.stderr)
        self.assertIn(says, r.stderr)


class BoardFolder(BoardCase):
    def test_a_missing_board_folder_is_one_line(self):
        shutil.rmtree(self.board)
        self.refused(self.t("search", "status=todo"), "no board folder at " + self.board)

    def test_a_board_path_that_is_a_file_is_refused(self):
        shutil.rmtree(self.board)
        self.file(os.path.join(".claude", "90north-develop", "board"), "not a folder")
        self.refused(self.t("get", "TASK-1"), "no board folder at " + self.board)

    def test_a_card_or_a_board_whose_mode_forbids_reading_is_skipped_or_named(self):
        """The one test that needs file modes: nothing else makes an existing file or folder unreadable."""
        self.assertFalse(AS_ROOT, "run this suite as a normal user: root reads a file and a folder of mode 000, "
                                  "so the unreadable card and the unreadable board cannot be made for it")
        self.mode(self.card_path("TASK-2"), 0)
        r = self.t("search", "status=todo")
        self.assertEqual((r.returncode, r.stdout.split(" | ")[0]), (0, "TASK-1"), r.stderr)
        self.assertIn("WARN TASK-2.md skipped", r.stderr)
        self.refused(self.t("get", "TASK-2"), "Permission denied")
        self.mode(self.board, 0)
        self.refused(self.t("get", "TASK-1"), "not readable")
        self.refused(self.t("search", "status=todo"), "not readable")

    def test_a_write_the_file_system_refuses_keeps_the_card_and_names_it(self):
        key = "A" * 243 + "-1"  # the card's file name fits in 255 bytes; the name of its temp file does not
        path, md = self.card_path(key), self.file("c.md", "x\n")
        with open(path, "w") as fh:
            fh.write(card("long key"))
        before = read(path)
        for args in (["edit", key, "--add-label", "x"], ["transition", key, "review"], ["comment", key, md]):
            self.refused(self.t(*args), "cannot write %s (File name too long); the card is unchanged" % path)
        self.assertEqual(read(path), before)
        self.assertEqual(sorted(os.listdir(self.board)), [key + ".md", "TASK-1.md", "TASK-2.md"])

    def test_a_direct_call_without_develop_dir_is_a_usage_error(self):
        env = {k: v for k, v in self.env.items() if k != "DEVELOP_DIR"}
        r = subprocess.run([sys.executable, "-I", LOCAL_BOARD, "search", "status=todo"],
                           env=env, capture_output=True, text=True)
        self.refused(r, "DEVELOP_DIR", code=2)

    def test_a_direct_call_without_a_verb_lists_the_verbs(self):
        r = subprocess.run([sys.executable, "-I", LOCAL_BOARD], env=self.env, capture_output=True, text=True)
        self.refused(r, "search|get|card|edit|transition|comment|attach|download", code=2)

    def test_a_relative_develop_dir_finds_its_board(self):
        env = dict(self.env, DEVELOP_DIR=os.path.join(".claude", "90north-develop"))
        r = run(["search", "status=todo"], self.root, env)
        self.assertEqual((r.returncode, [line.split(" | ")[0] for line in r.stdout.splitlines()]),
                         (0, ["TASK-2", "TASK-1"]), r.stderr)

    def test_files_that_are_not_cards_are_ignored_without_a_warning(self):
        self.file(os.path.join(".claude", "90north-develop", "board", "README.md"), "# notes, not a card\n")
        self.file(os.path.join(".claude", "90north-develop", "board", "TASK-9.txt"), "not markdown\n")
        r = self.t("search", "status=todo")
        self.assertEqual((r.returncode, r.stderr.strip()), (0, "# 2 issue(s)"))


class BrokenCards(BoardCase):
    def test_a_card_that_is_not_utf8_is_refused_in_one_line_by_every_verb(self):
        self.file(os.path.join(".claude", "90north-develop", "board", "TASK-2.md"), NOT_UTF8)
        md, clip = self.file("c.md", "hello\n"), self.file("clip.mp4", b"12")
        for args in (["get", "TASK-2"], ["card", "TASK-2"], ["edit", "TASK-2", "--add-label", "x"],
                     ["transition", "TASK-2", "review"], ["comment", "TASK-2", md], ["attach", "TASK-2", clip]):
            self.refused(self.t(*args), "TASK-2.md is not UTF-8 text")
        with open(self.card_path("TASK-2"), "rb") as fh:
            self.assertEqual(fh.read(), NOT_UTF8)

    def test_a_link_to_a_card_that_is_not_utf8_is_one_line(self):
        self.file(os.path.join(".claude", "90north-develop", "board", "TASK-2.md"), NOT_UTF8)
        with open(self.card_path("TASK-1"), "w") as fh:
            fh.write(card("first").replace("links:\n", "links: TASK-2\n"))
        self.refused(self.t("card", "TASK-1"), "TASK-2.md is not UTF-8 text")

    def test_search_skips_a_card_that_is_not_utf8_and_lists_the_rest(self):
        self.file(os.path.join(".claude", "90north-develop", "board", "TASK-2.md"), NOT_UTF8)
        r = self.t("search", "status=todo")
        self.assertEqual((r.returncode, r.stdout.split(" | ")[0]), (0, "TASK-1"), r.stderr)
        self.assertIn("WARN TASK-2.md skipped", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_a_header_line_without_a_colon_names_the_line(self):
        with open(self.card_path("TASK-2"), "w") as fh:
            fh.write("---\ntitle: ok\njust words\n---\n\n## Comments\n")
        self.refused(self.t("get", "TASK-2"), "TASK-2 line 3: expected 'name: value', got 'just words'")

    def test_a_header_that_never_closes_or_an_empty_file_is_refused(self):
        for text in ("---\ntitle: x\n", ""):
            with open(self.card_path("TASK-2"), "w") as fh:
                fh.write(text)
            self.refused(self.t("card", "TASK-2"), "TASK-2: a card starts with a --- header block")

    def test_a_card_with_no_header_keys_still_reads_moves_and_takes_a_comment(self):
        with open(self.card_path("TASK-2"), "w") as fh:
            fh.write("---\n---\n")
        self.assertEqual(self.t("card", "TASK-2").stdout.splitlines(), ["TASK-2  [ / ]", "LABELS: (none)"])
        self.assertEqual(self.t("search", "-status=done").stdout.splitlines()[-1].split(" | ")[0], "TASK-2")
        self.assertEqual(self.t("transition", "TASK-2", "review").stdout.strip(), "TASK-2:  → review")
        self.assertEqual(self.t("comment", "TASK-2", self.file("c.md", "seen\n")).returncode, 0)
        self.assertEqual(self.t("card", "TASK-2").stdout.splitlines()[0], "TASK-2  [ / review]")

    def test_a_status_outside_local_statuses_can_be_listed_and_moved(self):
        with open(self.card_path("TASK-2"), "w") as fh:
            fh.write(card("odd", status="shipped"))
        listed = self.t("transition", "TASK-2", "--list")
        self.assertEqual((listed.returncode, "← now" in listed.stdout), (0, False))
        self.assertEqual(self.t("transition", "TASK-2", "todo").stdout.strip(), "TASK-2: shipped → todo")

    def test_a_crlf_card_is_read_and_written_back_with_lf(self):
        self.file(os.path.join(".claude", "90north-develop", "board", "TASK-2.md"),
                  card("windows", body="## Description\nx\n").replace("\n", "\r\n"))
        self.assertEqual(self.t("card", "TASK-2", "description").stdout.splitlines(),
                         ["TASK-2  [bug / todo]", "LABELS: ai-queue", "FIELD description: x"])
        self.assertEqual(self.t("edit", "TASK-2", "--add-label", "seen").returncode, 0)
        with open(self.card_path("TASK-2"), "rb") as fh:
            after = fh.read()
        self.assertNotIn(b"\r", after)
        self.assertIn(b"labels: ai-queue, seen\n", after)


class Keys(BoardCase):
    def test_every_verb_refuses_a_key_that_has_no_card(self):
        md, clip, out = self.file("c.md", "x\n"), self.file("clip.mp4", b"12"), os.path.join(self.root, "out")
        for args in (["get", "NOPE-9"], ["card", "NOPE-9"], ["edit", "NOPE-9", "--add-label", "x"],
                     ["transition", "NOPE-9", "todo"], ["transition", "NOPE-9", "--list"], ["comment", "NOPE-9", md],
                     ["attach", "NOPE-9", clip], ["download", "NOPE-9", out]):
            self.refused(self.t(*args), "no card NOPE-9 at " + self.card_path("NOPE-9"))
        self.assertFalse(os.path.exists(out))
        self.assertEqual(sorted(os.listdir(self.board)), ["TASK-1.md", "TASK-2.md"])

    def test_wrong_argument_counts_print_the_verbs_usage(self):
        for args in (["search"], ["search", "a=b", "x", "y"], ["get"], ["get", "TASK-1", "x"], ["card"],
                     ["card", "TASK-1", "a", "b"], ["edit"], ["edit", "TASK-1"], ["transition", "TASK-1"],
                     ["comment", "TASK-1"], ["attach", "TASK-1"], ["download", "TASK-1"]):
            self.refused(self.t(*args), "usage: tracker.sh " + args[0], code=2)

    def test_field_names_are_checked_before_anything_is_printed(self):
        for names in ("Bad Name", "severity,,rank", ""):
            for r in (self.t("search", "status=todo", names), self.t("card", "TASK-1", names)):
                self.refused(r, "field names are comma-separated", code=2)
                self.assertEqual(r.stdout, "")


class Search(BoardCase):
    def test_a_malformed_query_or_age_is_one_line_and_lists_nothing(self):
        for query, says in (('title="no end', "query: No closing quotation"), ("age>2y", "query: bad term 'age>2y'"),
                            ("age>h", "query: bad term 'age>h'"), ("status", "query: bad term 'status'"),
                            ("sort=", "query: sort=<field> or sort=-<field>"), ("Status=todo", "query: bad term"),
                            ("age>" + "9" * 5000 + "d", "query age: a number of 5000 digits is too long")):
            r = self.t("search", query)
            self.refused(r, says)
            self.assertEqual(r.stdout, "")

    def test_a_card_whose_rank_is_too_long_to_be_a_number_is_listed_last(self):
        with open(self.card_path("TASK-2"), "w") as fh:
            fh.write(card("huge rank", rank="9" * 5000))
        r = self.t("search", "status=todo")
        self.assertEqual((r.returncode, [line.split(" | ")[0] for line in r.stdout.splitlines()]),
                         (0, ["TASK-1", "TASK-2"]), r.stderr[-300:])


class Attach(BoardCase):
    def test_a_source_that_is_missing_a_folder_or_unreadable_attaches_nothing(self):
        good, folder = self.file("ok.txt", "ok"), os.path.join(self.root, "folder")
        os.makedirs(folder)
        loop = os.path.join(self.root, "loop.mp4")
        os.symlink(loop, loop)  # a link to itself: nobody can read it, whatever the user
        for bad in (os.path.join(self.root, "nope.mp4"), folder, folder + os.sep, good + os.sep, loop):
            self.refused(self.t("attach", "TASK-1", good, bad), bad + " is not a file this user can read")
        self.assertFalse(os.path.exists(os.path.join(self.board, "TASK-1")))

    def test_a_file_where_the_attachment_folder_belongs_is_one_line(self):
        self.file(os.path.join(".claude", "90north-develop", "board", "TASK-1"), "a file, not a folder")
        self.refused(self.t("attach", "TASK-1", self.file("clip.mp4", b"12")), "File exists")
        self.assertEqual(read(os.path.join(self.board, "TASK-1")), "a file, not a folder")

    def test_two_sources_with_one_name_attach_nothing(self):
        os.makedirs(os.path.join(self.root, "a"))
        one, two = self.file("clip.mp4", "1"), self.file(os.path.join("a", "clip.mp4"), "2")
        self.refused(self.t("attach", "TASK-1", one, two), "clip.mp4 is given twice")
        self.assertFalse(os.path.exists(os.path.join(self.board, "TASK-1")))

    def test_two_names_the_volume_treats_as_one_never_lose_the_first_take(self):
        os.makedirs(os.path.join(self.root, "a"))
        first, second = self.file("take.mp4", "first"), self.file(os.path.join("a", "TAKE.mp4"), "second")
        r, folder = self.t("attach", "TASK-1", first, second), os.path.join(self.board, "TASK-1")
        self.assertEqual(read(os.path.join(folder, "take.mp4")), "first")
        if len(os.listdir(folder)) == 1:  # a volume that ignores case: the second name is the first file
            self.refused(r, "TASK-1/TAKE.mp4 exists")
        else:
            self.assertEqual((r.returncode, read(os.path.join(folder, "TAKE.mp4"))), (0, "second"))

    def test_a_readable_source_that_is_not_a_regular_file_is_still_copied(self):
        r = self.t("attach", "TASK-1", os.devnull)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "attached null → TASK-1/null 0 bytes"), r.stderr)

    def test_a_named_pipe_is_refused_by_the_copy_and_leaves_nothing(self):
        pipe = os.path.join(self.root, "take.fifo")
        os.mkfifo(pipe)
        self.refused(self.t("attach", "TASK-1", pipe), "is a named pipe")
        self.assertEqual(os.listdir(os.path.join(self.board, "TASK-1")), [])

    def test_an_existing_name_is_never_overwritten_and_keeps_its_bytes(self):
        self.assertEqual(self.t("attach", "TASK-1", self.file("clip.mp4", "first take")).returncode, 0)
        self.refused(self.t("attach", "TASK-1", self.file("clip.mp4", "second take")), "TASK-1/clip.mp4 exists")
        self.assertEqual(read(os.path.join(self.board, "TASK-1", "clip.mp4")), "first take")


class Download(BoardCase):
    def setUp(self):
        super().setUp()
        os.makedirs(os.path.join(self.board, "TASK-1"))
        for name in ("a.txt", "b.txt"):
            self.file(os.path.join(".claude", "90north-develop", "board", "TASK-1", name), name)
        self.out = os.path.join(self.root, "out")

    def test_named_files_only_and_an_existing_empty_folder_is_fine(self):
        os.makedirs(self.out)
        r = self.t("download", "TASK-1", self.out, "b.txt")
        self.assertEqual((r.returncode, r.stdout.strip()),
                         (0, "downloaded TASK-1/b.txt → " + os.path.join(self.out, "b.txt")))
        self.assertEqual(os.listdir(self.out), ["b.txt"])

    def test_a_name_that_is_not_an_attachment_stops_before_the_folder_is_made(self):
        os.makedirs(os.path.join(self.board, "TASK-1", "sub"))
        for names in (["nope.txt"], ["a.txt", "nope.txt"], [".."], ["sub"], []):
            r = self.t("download", "TASK-1", self.out, *names)
            self.refused(r, "no attachment file TASK-1/")
            self.assertFalse(os.path.exists(self.out), names)

    def test_attachments_whose_card_file_is_gone_can_still_be_downloaded(self):
        os.rename(self.card_path("TASK-1"), os.path.join(self.root, "TASK-1.md.moved"))
        r = self.t("download", "TASK-1", self.out, "a.txt")
        copied = os.listdir(self.out) if os.path.isdir(self.out) else None
        self.assertEqual((r.returncode, copied), (0, ["a.txt"]), r.stderr)

    def test_a_card_without_attachments_gives_an_empty_folder(self):
        r = self.t("download", "TASK-2", self.out)
        self.assertEqual((r.returncode, r.stdout, os.listdir(self.out)), (0, "", []))

    def test_a_target_that_is_a_file_or_lies_below_one_is_one_line(self):
        taken = self.file("taken", "x")
        self.refused(self.t("download", "TASK-1", taken), "File exists")
        self.refused(self.t("download", "TASK-1", os.path.join(taken, "out")), "Not a directory")
        self.assertEqual(read(taken), "x")


class Edit(BoardCase):
    def test_malformed_flags_are_usage_errors_and_write_nothing(self):
        before = read(self.card_path("TASK-1"))
        for flags in (["--field", "severity"], ["--field", "=v"], ["--field-md", "heading"], ["--field"],
                      ["--zap", "x"], ["--add-label", "a", "stray"], ["--dry-run"]):
            self.refused(self.t("edit", "TASK-1", *flags), "usage: tracker.sh edit KEY", code=2)
        self.assertEqual(read(self.card_path("TASK-1")), before)

    def test_a_field_md_file_that_is_missing_a_folder_or_not_utf8_is_one_line(self):
        before = read(self.card_path("TASK-1"))
        self.refused(self.t("edit", "TASK-1", "--field-md", "Notes=" + os.path.join(self.root, "nope.md")),
                     "No such file or directory")
        self.refused(self.t("edit", "TASK-1", "--field-md", "Notes=" + self.root), "Is a directory")
        bad = self.file("bad.md", b"caf\xe9\n")
        self.refused(self.t("edit", "TASK-1", "--field-md", "Notes=" + bad), bad + " is not UTF-8 text")
        self.assertEqual(read(self.card_path("TASK-1")), before)

    def test_a_section_heading_is_one_line(self):
        before, md = read(self.card_path("TASK-1")), self.file("s.md", "text\n")
        for heading in ("Notes\n## Comments", "Notes\nmore", "Notes\rmore"):
            self.refused(self.t("edit", "TASK-1", "--field-md", heading + "=" + md), "one line")
        self.assertEqual(read(self.card_path("TASK-1")), before)

    def test_labels_with_illegal_characters_are_refused_and_nothing_is_written(self):
        before = read(self.card_path("TASK-1"))
        for label in ("two words", "a,b", "", "tab\there", "new\nline"):
            self.refused(self.t("edit", "TASK-1", "--add-label", "ok", "--add-label", label), "label ")
        self.assertEqual(read(self.card_path("TASK-1")), before)

    def test_a_value_whose_bytes_are_not_utf8_is_refused_and_leaves_no_temp_file(self):
        before = read(self.card_path("TASK-1"))
        r = subprocess.run([TRACKER.encode(), b"edit", b"TASK-1", b"--field", b"severity=\xff"],
                           cwd=self.root, env=self.env, capture_output=True)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertNotIn(b"Traceback", r.stderr)
        self.assertIn(b"not UTF-8", r.stderr)
        self.assertEqual(read(self.card_path("TASK-1")), before)
        self.assertEqual(sorted(os.listdir(self.board)), ["TASK-1.md", "TASK-2.md"])


class Transition(BoardCase):
    def test_a_never_use_status_is_still_a_listed_status(self):
        """`done` is never-use by the loops' config, not by this script: the script accepts any listed status."""
        r = self.t("transition", "TASK-1", "done")
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "TASK-1: todo → done"))

    def test_an_unknown_status_writes_nothing(self):
        before = read(self.card_path("TASK-1"))
        self.refused(self.t("transition", "TASK-1", "shipped"), "status 'shipped' is not in LOCAL_STATUSES")
        self.refused(self.t("transition", "TASK-1", ""), "status '' is not in LOCAL_STATUSES")
        self.assertEqual(read(self.card_path("TASK-1")), before)


class Comment(BoardCase):
    def test_a_comment_file_that_is_missing_a_folder_or_not_utf8_is_one_line(self):
        before = read(self.card_path("TASK-1"))
        self.refused(self.t("comment", "TASK-1", os.path.join(self.root, "nope.md")), "No such file or directory")
        self.refused(self.t("comment", "TASK-1", self.root), "Is a directory")
        bad = self.file("bad.md", b"\xff\xfe")
        self.refused(self.t("comment", "TASK-1", bad), bad + " is not UTF-8 text")
        self.assertEqual(read(self.card_path("TASK-1")), before)

    def test_a_video_path_the_link_cannot_hold_is_refused(self):
        before = read(self.card_path("TASK-1"))
        for path in ("../../x]y.mp4", "TASK-1/a(b).mp4", "TASK-1/[take].mp4"):
            self.refused(self.t("comment", "TASK-1", self.file("c.md", "proof\n::video %s\n" % path)), "::video")
        self.assertEqual(read(self.card_path("TASK-1")), before)

    def test_a_video_path_with_a_nul_byte_is_refused_in_one_line(self):
        before = read(self.card_path("TASK-1"))
        self.refused(self.t("comment", "TASK-1", self.file("c.md", b"::video TASK-1/a\x00b.mp4\n")), "nothing written")
        self.assertEqual(read(self.card_path("TASK-1")), before)

    def test_a_video_that_is_a_folder_counts_as_missing(self):
        os.makedirs(os.path.join(self.board, "TASK-1"))
        self.refused(self.t("comment", "TASK-1", self.file("c.md", "::video TASK-1\n")), "missing TASK-1")

    def test_replacing_a_comment_that_is_not_there_writes_nothing(self):
        before = read(self.card_path("TASK-1"))
        self.refused(self.t("comment", "TASK-1", self.file("c.md", "x\n"), "c7"), "TASK-1 has no comment c7")
        self.assertEqual(read(self.card_path("TASK-1")), before)


class AtomicWrite(BoardCase):
    """In-process, so the moment of the rename can be observed."""

    def main(self, *args):
        out, err = io.StringIO(), io.StringIO()
        env = {"DEVELOP_DIR": self.dl, "LOCAL_BOARD": "", "LOCAL_STATUSES": ""}
        with mock.patch.dict(os.environ, env), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            return local_board.main(list(args)), out.getvalue(), err.getvalue()

    def test_the_new_card_is_whole_in_a_temp_file_beside_the_old_one_before_the_rename(self):
        path, before, seen, real = self.card_path("TASK-1"), read(self.card_path("TASK-1")), [], os.replace

        def watch(src, dst):
            seen.append((os.path.dirname(src), dst, read(dst), read(src)))
            real(src, dst)

        with mock.patch("os.replace", side_effect=watch):
            code, _, _ = self.main("edit", "TASK-1", "--add-label", "atomic")
        self.assertEqual((code, len(seen)), (0, 1))
        folder, target, old_at_rename, new_at_rename = seen[0]
        self.assertEqual((folder, target, old_at_rename), (self.board, path, before))
        self.assertEqual(new_at_rename, read(path))
        self.assertIn("labels: ai-queue, atomic\n", new_at_rename)
        self.assertEqual(sorted(os.listdir(self.board)), ["TASK-1.md", "TASK-2.md"])

    def test_a_write_that_fails_keeps_the_old_card_and_removes_the_temp_file(self):
        before = read(self.card_path("TASK-1"))
        full = OSError(errno.ENOSPC, "No space left on device")
        for verb in (["edit", "TASK-1", "--add-label", "x"], ["transition", "TASK-1", "review"],
                     ["comment", "TASK-1", self.file("c.md", "x\n")]):
            with mock.patch("os.replace", side_effect=full):
                code, out, err = self.main(*verb)
            self.assertEqual((code, out), (1, ""), verb)
            self.assertEqual(err, "error: cannot write %s (No space left on device); the card is unchanged\n"
                             % self.card_path("TASK-1"))
            self.assertEqual(read(self.card_path("TASK-1")), before)
            self.assertEqual(sorted(os.listdir(self.board)), ["TASK-1.md", "TASK-2.md"])

    def test_a_copy_that_fails_half_way_leaves_no_file_to_block_the_retry(self):
        clip, real = self.file("clip.mp4", "0123456789"), shutil.copy2

        def half(src, dst):
            with open(dst, "w") as fh:
                fh.write("01234")
            raise OSError(errno.EFBIG, "File too large")

        with mock.patch("shutil.copy2", side_effect=half):
            code, out, err = self.main("attach", "TASK-1", clip)
        self.assertEqual((code, out, err), (1, "", "error: [Errno 27] File too large\n"))
        self.assertEqual(os.listdir(os.path.join(self.board, "TASK-1")), [])
        with mock.patch("shutil.copy2", side_effect=real):
            self.assertEqual(self.main("attach", "TASK-1", clip)[:2],
                             (0, "attached clip.mp4 → TASK-1/clip.mp4 10 bytes\n"))

    def test_an_interrupt_after_the_temp_file_is_written_leaves_the_old_card(self):
        before = read(self.card_path("TASK-1"))
        with mock.patch("os.chmod", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.main("transition", "TASK-1", "review")
        self.assertEqual(read(self.card_path("TASK-1")), before)
        self.assertEqual(sorted(os.listdir(self.board)), ["TASK-1.md", "TASK-2.md"])


if __name__ == "__main__":
    unittest.main()
