"""What the local board prints when the output side misbehaves: a closed or broken stdout, a locale, odd bytes.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_local_board_failures import LOCAL_BOARD, BoardCase  # noqa: E402
from test_tracker import TRACKER, card, read  # noqa: E402


def reader_gone(cmd, cwd, env, read_first=0):
    """Run `cmd` with a stdout whose reader leaves (after `read_first` bytes); returns (exit code, stderr)."""
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if read_first:
        p.stdout.read(read_first)
    p.stdout.close()
    err = p.stderr.read().decode("utf-8")
    p.stderr.close()
    return p.wait(), err


class Stdout(BoardCase):
    def closed(self, *args):
        return subprocess.run(["bash", "-c", 'exec "$0" "$@" >&-', TRACKER] + list(args),
                              cwd=self.root, env=self.env, capture_output=True, text=True)

    def test_a_closed_stdout_fails_no_verb(self):
        for args in (["get", "TASK-1"], ["edit", "TASK-1", "--dry-run", "--add-label", "x"],
                     ["transition", "TASK-1", "review"]):
            r = self.closed(*args)
            self.assertEqual((r.returncode, r.stderr), (0, ""), args)
        self.assertIn("status: review", read(self.card_path("TASK-1")))

    def test_a_reader_that_left_is_one_line_whether_the_card_is_small_or_large(self):
        with open(self.card_path("TASK-2"), "w") as fh:
            fh.write(card("large", body="## Description\n" + ("x" * 99 + "\n") * 4000))
        small = "error: get finished, but its output could not be written: Broken pipe\n"
        for key, read_first, says in (("TASK-1", 0, small), ("TASK-2", 10, "error: [Errno 32] Broken pipe\n")):
            code, err = reader_gone([TRACKER, "get", key], self.root, self.env, read_first)
            self.assertEqual((code, err), (1, says), key)

    def test_a_verb_that_wrote_says_it_finished_when_its_reader_left(self):
        code, err = reader_gone([TRACKER, "comment", "TASK-1", self.file("c.md", "once\n")], self.root, self.env)
        self.assertEqual((code, err),
                         (1, "error: comment finished, but its output could not be written: Broken pipe\n"))
        self.assertEqual(read(self.card_path("TASK-1")).count("### c1 · "), 1)

    def test_a_refusal_stays_the_one_line_when_the_reader_left_as_well(self):
        with open(self.card_path("TASK-1"), "w") as fh:
            fh.write(card("first").replace("links:\n", "links: TASK-2\n"))
        with open(self.card_path("TASK-2"), "w") as fh:
            fh.write("no header\n")
        code, err = reader_gone([TRACKER, "card", "TASK-1"], self.root, self.env)
        self.assertEqual((code, err), (1, "error: TASK-2: a card starts with a --- header block\n"))

    def test_a_stdout_file_that_cannot_grow_is_one_line_too(self):
        env = {k: v for k, v in self.env.items() if k != "COVERAGE_PROCESS_START"}  # its data file cannot grow either
        r = subprocess.run(["bash", "-c", 'ulimit -f 0; exec "$0" "$@" > full.txt', TRACKER, "get", "TASK-1"],
                           cwd=self.root, env=env, capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stderr),
                         (1, "error: get finished, but its output could not be written: File too large\n"))

    def test_results_still_reach_stdout_when_nobody_reads_stderr(self):
        results = os.path.join(self.root, "results.txt")
        with open(results, "wb") as out:
            p = subprocess.Popen([TRACKER, "search", "status=todo"], cwd=self.root, env=self.env,
                                 stdout=out, stderr=subprocess.PIPE)
            p.stderr.close()
            code = p.wait()
        self.assertEqual((code, [line.split(" | ")[0] for line in read(results).splitlines()]),
                         (1, ["TASK-2", "TASK-1"]))

    def test_a_stdout_that_cannot_show_the_arrow_gets_an_escape_and_the_verb_still_succeeds(self):
        env = dict(self.env, DEVELOP_DIR=self.dl, PYTHONIOENCODING="ascii")
        r = subprocess.run([sys.executable, LOCAL_BOARD, "transition", "TASK-1", "review"],
                           env=env, capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "TASK-1: todo \\u2192 review"), r.stderr)
        self.assertIn("status: review", read(self.card_path("TASK-1")))

    def test_bytes_that_are_not_text_still_pass_through_a_dry_run_in_the_c_locale(self):
        env = dict(self.env, LC_ALL="C")
        r = subprocess.run([TRACKER.encode(), b"edit", b"TASK-1", b"--dry-run", b"--field", b"severity=\xff"],
                           cwd=self.root, env=env, capture_output=True)
        self.assertEqual((r.returncode, r.stderr), (0, b""))
        self.assertIn(b"severity: \xff\n", r.stdout)


class OneLine(BoardCase):
    def test_a_line_break_in_an_argument_or_a_link_never_adds_a_second_error_line(self):
        fake = "nope\nerror: fake"
        for folder in (os.path.join(self.board, "TASK-1"), os.path.join(self.root, "taken")):
            os.makedirs(folder)
        out, md = os.path.join(self.root, "out"), self.file("c.md", "x\n")
        link = self.file("l.md", "[video: x](TASK-1/%s)\n" % fake)
        in_the_way = self.file(os.path.join("taken", fake), "a file where the folder should go")
        for args in (["attach", "TASK-1", fake], ["download", "TASK-1", out, fake], ["comment", "TASK-1", md, fake],
                     ["comment", "TASK-1", link], ["download", "TASK-1", in_the_way]):
            self.refused(self.t(*args), "nope\\nerror: fake")


if __name__ == "__main__":
    unittest.main()
