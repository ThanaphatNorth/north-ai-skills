"""The hook that holds n-dev's finish gate: it reads what the session really did and reminds once."""
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

GATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "finish_gate.py")
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
           GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
LONG_AGO = "@1577836800 +0000"
LAUNCHED = "Async agent launched successfully. The agent is working in the background."


class GateCase(unittest.TestCase):
    """A git repo with one old commit, and a session transcript the test fills in the way Claude Code writes it:
    one line per message, each with a timestamp, tool calls answered by tool results with the same id."""
    stamped = True

    def setUp(self):
        self.repo = os.path.realpath(tempfile.mkdtemp(prefix="ndev-gate-"))
        self.clock = time.time() - 3600.0  # the session started an hour ago; every step moves the clock on
        self.git("init", "-q", "-b", "main")
        self.write("src/price.py", "def price():\n    return 1\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base", date=LONG_AGO)
        self.events = []
        self.say("user", "do the task")

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def tick(self):
        self.clock += 10.0
        return self.clock

    def git(self, *args, date=None):
        env = dict(ENV, GIT_COMMITTER_DATE=date, GIT_AUTHOR_DATE=date) if date else ENV
        subprocess.run(["git", *args], cwd=self.repo, env=env, check=True, capture_output=True)

    def path(self, rel):
        return os.path.join(self.repo, rel)

    def write(self, rel, text, when=None):
        """Write a file; its modification time is the session clock (or `when`)."""
        os.makedirs(os.path.dirname(self.path(rel)), exist_ok=True)
        with open(self.path(rel), "w") as fh:
            fh.write(text)
        stamp = self.tick() if when is None else when
        os.utime(self.path(rel), (stamp, stamp))

    def say(self, role, content):
        line = {"type": role, "message": {"role": role, "content": content}}
        if self.stamped:
            moment = datetime.datetime.fromtimestamp(self.tick(), datetime.timezone.utc)
            line["timestamp"] = moment.isoformat(timespec="milliseconds").replace("+00:00", "Z")
        self.events.append(line)
        return line

    def call(self, name, **tool_input):
        call_id = "toolu_%02d" % len(self.events)
        self.say("assistant", [{"type": "tool_use", "id": call_id, "name": name, "input": tool_input}])
        return call_id

    def answer(self, call_id, text="ok"):
        self.say("user", [{"type": "tool_result", "tool_use_id": call_id, "content": [{"type": "text", "text": text}]}])

    def edit(self, rel, text="x = 1\n", tool_name="Edit"):
        """The session edits a file with a file tool: the call, the file on disk, the answer."""
        call_id = self.call(tool_name, file_path=self.path(rel))
        self.write(rel, text)
        self.answer(call_id)

    def shell_write(self, rel, text="x = 1\n"):
        """The session writes a file with a shell here-document, as agents often do."""
        call_id = self.call("Bash", command="cat > %s <<'EOF'\n%sEOF" % (rel, text))
        self.write(rel, text)
        self.answer(call_id)

    def bash(self, command, result="ok"):
        self.answer(self.call("Bash", command=command), result)

    def check(self):
        self.bash("python3 /skills/n-dev/scripts/structure_check.py --base main", "RESULT: clean")

    def commit(self):
        call_id = self.call("Bash", command="git checkout -q -b feat/x && git add -A && git commit -q -m work")
        self.git("checkout", "-q", "-B", "feat/x")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "work", date="@%d +0000" % self.tick())
        self.answer(call_id)

    def review(self, tool_name="Agent", background=False, finished=True):
        """A reviewer subagent: in the foreground its answer is the tool result; in the background the tool result
        only says it started, and a task notification brings the answer later."""
        call_id = self.call(tool_name, description="Review the diff", prompt="review this diff through three lenses")
        if not background:
            self.answer(call_id, "0 blockers, 0 should-fix, 1 note")
        else:
            self.answer(call_id, LAUNCHED)
            if finished:
                self.say("user", "<task-notification>\n<task-id>a1</task-id>\n<tool-use-id>%s</tool-use-id>\n"
                                 "<status>completed</status>\n<result>0 blockers</result>\n</task-notification>" % call_id)
        return call_id

    def run_hook(self, payload, stdin=None, env=ENV):
        transcript = os.path.join(self.repo, ".git", "transcript.jsonl")
        with open(transcript, "w") as fh:
            fh.write("".join((e if isinstance(e, str) else json.dumps(e)) + "\n" for e in self.events))
        payload = dict({"cwd": self.repo, "transcript_path": transcript}, **payload)
        proc = subprocess.run([sys.executable, "-I", GATE], input=json.dumps(payload) if stdin is None else stdin,
                              capture_output=True, text=True, env=env)
        return proc.returncode, proc.stderr

    def stop(self, active=False, cwd=None, stdin=None):
        return self.run_hook({"hook_event_name": "Stop", "stop_hook_active": active, "cwd": cwd or self.repo}, stdin)

    def before_commit(self, command="git add -A && git commit -q -m work", agent=None):
        payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
        if agent:
            payload["agent_type"] = agent
        return self.run_hook(payload)


class Reminds(GateCase):
    def test_code_changed_and_nothing_else_done(self):
        self.edit("src/price.py")
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("structure check", err)
        self.assertIn("commit", err)
        self.assertNotIn("reviewer", err)  # one source file is Tiny work: no review

    def test_code_written_through_the_shell_counts_like_any_other(self):
        self.shell_write("src/price.py", "def price():\n    return 2\n")
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("structure check", err)
        self.assertIn("src/price.py", err)

    def test_a_new_file_the_session_named_only_by_its_file_name_is_its_change(self):
        call_id = self.call("Bash", command="cd src && cat > coupon.py <<'EOF'\nx = 1\nEOF")
        self.write("src/coupon.py", "x = 1\n")
        self.answer(call_id)
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("src/coupon.py", err)

    def test_a_tracked_file_a_tool_rewrote_is_the_sessions_change(self):
        call_id = self.call("Bash", command="npx prettier --write .")
        self.write("src/price.py", "def price():\n    return 1  # formatted\n")
        self.answer(call_id)
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("src/price.py", err)

    def test_the_reminder_asks_for_the_whole_report_again(self):
        self.edit("src/price.py")
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("write the report again in full", err)

    def test_check_ran_but_the_change_is_not_committed(self):
        self.edit("src/price.py")
        self.check()
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("commit", err)
        self.assertNotIn("structure check", err)

    def test_check_that_ran_before_the_last_edit_does_not_count(self):
        self.edit("src/price.py")
        self.check()
        self.edit("src/price.py", "y = 2\n")
        self.commit()
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("structure check", err)
        self.assertNotIn("commit your", err)

    def test_check_that_ran_before_the_last_shell_write_does_not_count(self):
        self.shell_write("src/price.py")
        self.check()
        self.shell_write("src/price.py", "y = 2\n")
        self.commit()
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("structure check", err)

    def test_two_source_files_need_a_reviewer(self):
        self.edit("src/coupon.py", tool_name="Write")
        self.edit("src/price.py")
        self.edit("tests/test_coupon.py", tool_name="Write")
        self.check()
        self.commit()
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("reviewer", err)
        self.assertNotIn("structure check", err)

    def test_two_shell_written_source_files_need_a_reviewer_even_after_the_commit(self):
        self.shell_write("src/coupon.py")
        self.shell_write("src/price.py", "y = 2\n")
        self.check()
        self.commit()
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("reviewer", err)
        self.assertIn("2 source files", err)
        self.assertNotIn("Commit your", err)

    def test_a_subagent_that_ran_before_the_code_existed_is_not_the_review(self):
        self.answer(self.call("Agent", prompt="find code to reuse"), "nothing to reuse")
        self.edit("src/coupon.py", tool_name="Write")
        self.edit("src/price.py")
        self.check()
        self.commit()
        self.assertEqual(self.stop()[0], 2)

    def test_an_angle_bracket_in_a_commit_message_is_not_a_file_write(self):
        self.bash('git log -1 --format="%an <%ae>" && echo "Co-Authored-By: A <a@example.com>"')
        self.answer(self.call("Agent", prompt="find code to reuse"), "nothing to reuse")
        self.shell_write("src/coupon.py")
        self.shell_write("src/price.py", "y = 2\n")
        self.check()
        self.commit()
        code, err = self.stop()
        self.assertEqual(code, 2)  # the subagent ran before any code was written: it is not the review
        self.assertIn("reviewer", err)

    def test_a_builder_or_another_helper_is_not_the_reviewer(self):
        self.shell_write("src/coupon.py")
        self.shell_write("src/price.py", "y = 2\n")
        self.check()
        self.answer(self.call("Agent", subagent_type="90north-develop:dev-builder", description="Build WP-2",
                              prompt="build the work package test-first"), "DONE: 1 commit")
        self.assertEqual(self.before_commit()[0], 2)  # a subagent ran, but nobody read the diff as a reviewer
        self.commit()
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("reviewer", err)

    def test_a_builder_sent_back_with_review_findings_is_still_not_the_reviewer(self):
        self.shell_write("src/coupon.py")
        self.shell_write("src/price.py", "y = 2\n")
        self.check()
        self.answer(self.call("Agent", subagent_type="90north-develop:dev-builder", description="Fix round 1",
                              prompt="apply these review findings, test-first"), "DONE: 1 commit")
        self.assertEqual(self.before_commit()[0], 2)

    def test_the_reviewer_reminder_leaves_the_number_of_reviewers_to_step_6(self):
        self.shell_write("src/coupon.py")
        self.shell_write("src/price.py", "y = 2\n")
        self.check()
        self.commit()
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("step 6", err)
        self.assertNotIn("one fresh reviewer", err)  # a large diff gets one reviewer per lens: the hook does not count lines

    def test_a_call_written_twice_in_the_transcript_is_one_call(self):
        early = self.call("Agent", prompt="find code to reuse")
        self.answer(early, "nothing to reuse")
        self.shell_write("src/coupon.py")
        self.shell_write("src/price.py", "y = 2\n")
        self.check()
        self.commit()
        self.events.append(self.events[1])  # Claude Code also stores a copy of a request's messages
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("reviewer", err)

    def test_the_reminder_names_every_missing_step_and_how_to_decline(self):
        self.edit("src/coupon.py", tool_name="Write")
        self.edit("src/price.py")
        code, err = self.stop()
        self.assertEqual(code, 2)
        for word in ("structure check", "reviewer", "commit", "say why"):
            self.assertIn(word, err)


class LetsGo(GateCase):
    def test_everything_done_on_tiny_work(self):
        self.edit("src/price.py")
        self.edit("tests/test_price.py", tool_name="Write")
        self.check()
        self.commit()
        self.assertEqual(self.stop(), (0, ""))

    def test_everything_done_on_standard_work(self):
        self.edit("src/coupon.py", tool_name="Write")
        self.edit("src/price.py")
        self.check()
        self.review(tool_name="Task")
        self.commit()
        self.assertEqual(self.stop(), (0, ""))

    def test_everything_done_through_the_shell_with_a_background_reviewer(self):
        self.shell_write("src/coupon.py")
        self.shell_write("src/price.py", "y = 2\n")
        self.check()
        self.review(background=True)
        self.commit()
        self.assertEqual(self.stop(), (0, ""))

    def test_a_turn_that_ends_to_wait_for_the_reviewer_is_left_alone(self):
        self.shell_write("src/coupon.py")
        self.shell_write("src/price.py", "y = 2\n")
        self.review(background=True, finished=False)
        self.assertEqual(self.stop(), (0, ""))  # nothing is committed or checked yet: the reviewer comes first

    def test_it_reminds_once_only(self):
        self.edit("src/price.py")
        self.assertEqual(self.stop(active=True), (0, ""))

    def test_a_session_that_changed_no_file(self):
        self.bash("git log --oneline -3")
        self.assertEqual(self.stop(), (0, ""))

    def test_a_file_that_was_already_dirty_is_not_this_sessions_change(self):
        self.write("src/price.py", "def price():\n    return 3\n", when=self.clock - 600.0)
        self.write("src/old_draft.py", "x = 1\n", when=self.clock - 600.0)
        self.bash("git status --short")
        self.assertEqual(self.stop(), (0, ""))

    def test_files_a_tool_left_in_the_repo_are_not_the_sessions_change(self):
        self.shell_write("src/price.py", "def price():\n    return 2\n")
        self.check()
        self.commit()
        # tools write caches and settings as they run; a plain word such as "config" in a command names no file
        self.bash("git config user.name && npm test && aws sts get-caller-identity")
        for left_behind in (".config/git/ignore", ".aws/config", ".cache/v/lastfailed", "out/price.cpython-312.pyc"):
            self.write(left_behind, "x\n")
        self.assertEqual(self.stop(), (0, ""))

    def test_files_outside_the_repo_are_not_its_business(self):
        outside = os.path.join(tempfile.mkdtemp(prefix="ndev-out-"), "note.py")
        with open(outside, "w") as fh:
            fh.write("x = 1\n")
        self.answer(self.call("Write", file_path=outside))
        self.assertEqual(self.stop(), (0, ""))

    def test_docs_alone_are_not_code(self):
        self.edit("README.md", "# notes\n", tool_name="Write")
        self.shell_write("docs/guide.md", "text\n")
        self.assertEqual(self.stop(), (0, ""))

    def test_ignored_files_are_not_code(self):
        self.write(".gitignore", "build/\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "ignore", date=LONG_AGO)
        self.edit("build/out.py", tool_name="Write")
        self.assertEqual(self.stop(), (0, ""))

    def test_not_a_git_repo(self):
        plain = tempfile.mkdtemp(prefix="ndev-plain-")
        self.answer(self.call("Write", file_path=os.path.join(plain, "a.py")))
        self.assertEqual(self.stop(cwd=plain), (0, ""))

    def test_a_broken_line_in_the_transcript_is_passed_over(self):
        self.edit("src/price.py")
        self.events.append("this line is not a JSON object {")
        self.events.append("[1, 2]")
        code, err = self.stop()
        self.assertEqual(code, 2)  # the edit before the broken lines still counts
        self.assertIn("structure check", err)

    def test_a_machine_without_git_is_left_alone(self):
        self.edit("src/price.py")
        self.assertEqual(self.run_hook({"hook_event_name": "Stop"}, env=dict(ENV, PATH="")), (0, ""))

    def test_main_can_be_called_directly(self):
        sys.path.insert(0, os.path.dirname(GATE))
        import finish_gate
        self.assertEqual(finish_gate.main("not json"), 0)
        self.assertEqual(finish_gate.main(json.dumps({"stop_hook_active": True})), 0)

    def test_it_never_blocks_on_its_own_failure(self):
        self.assertEqual(self.stop(stdin="not json"), (0, ""))
        self.assertEqual(self.stop(stdin=json.dumps({"cwd": self.repo, "transcript_path": "/no/such/file"})), (0, ""))


class OddTranscripts(GateCase):
    """Whatever else is in the transcript, the hook reads what it knows and passes over the rest."""

    def test_blocks_it_does_not_know_are_passed_over(self):
        self.say("assistant", [{"type": "text", "text": "working on it"}, "a bare string", {"type": "thinking"}])
        self.edit("src/price.py")
        call_id = self.call("Bash", command="true")
        self.say("user", [{"type": "tool_result", "tool_use_id": call_id, "content": None}])
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("structure check", err)

    def test_a_timestamp_it_cannot_read_counts_as_none(self):
        self.events[0]["timestamp"] = "yesterday at noon"  # the session then starts at the next line that has one
        self.shell_write("src/price.py", "y = 2\n")
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("src/price.py", err)

    def test_a_deleted_file_cannot_be_dated_and_is_left_out_until_it_is_committed(self):
        self.bash("rm src/price.py")
        os.remove(self.path("src/price.py"))
        self.assertEqual(self.stop(), (0, ""))


class WithoutTimestamps(GateCase):
    """An older transcript has no timestamps: the hook then goes by the order of the file-tool edits."""
    stamped = False

    def test_check_before_the_last_edit_does_not_count(self):
        self.edit("src/price.py")
        self.check()
        self.edit("src/price.py", "y = 2\n")
        self.commit()
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("structure check", err)

    def test_everything_done_on_standard_work(self):
        self.edit("src/coupon.py", tool_name="Write")
        self.edit("src/price.py")
        self.check()
        self.review()
        self.commit()
        self.assertEqual(self.stop(), (0, ""))

    def test_two_source_files_need_a_reviewer(self):
        self.edit("src/coupon.py", tool_name="Write")
        self.edit("src/price.py")
        self.check()
        self.commit()
        code, err = self.stop()
        self.assertEqual(code, 2)
        self.assertIn("reviewer", err)


class CommitGate(GateCase):
    """Before a `git commit`: Standard work waits for its reviewer."""

    def standard_work(self):
        self.shell_write("src/coupon.py")
        self.shell_write("src/price.py", "y = 2\n")
        self.check()

    def test_standard_work_with_no_reviewer_is_held(self):
        self.standard_work()
        code, err = self.before_commit()
        self.assertEqual(code, 2)
        self.assertIn("n-dev review gate:", err)
        self.assertIn("Standard work", err)
        self.assertIn("Agent or Task tool", err)

    def test_a_reviewer_that_is_still_reading_holds_the_commit(self):
        self.standard_work()
        self.review(background=True, finished=False)
        code, err = self.before_commit()
        self.assertEqual(code, 2)
        self.assertIn("has not answered yet", err)

    def test_a_reviewer_that_answered_lets_the_commit_run(self):
        self.standard_work()
        self.review()
        self.assertEqual(self.before_commit(), (0, ""))

    def test_a_background_reviewer_that_finished_lets_the_commit_run(self):
        self.standard_work()
        self.review(background=True)
        self.assertEqual(self.before_commit("git -C . commit -q -m work"), (0, ""))

    def test_tiny_work_commits_without_a_review(self):
        self.shell_write("src/price.py", "y = 2\n")
        self.shell_write("tests/test_price.py")
        self.assertEqual(self.before_commit(), (0, ""))

    def test_the_commit_is_held_once(self):
        self.standard_work()
        code, err = self.before_commit()
        self.assertEqual(code, 2)
        self.bash("git add -A && git commit -q -m work", err)  # Claude Code hands the hook's words back as the answer
        self.assertEqual(self.before_commit(), (0, ""))

    def test_a_subagents_own_commit_is_never_held(self):
        self.standard_work()
        self.assertEqual(self.before_commit(agent="90north-develop:dev-builder"), (0, ""))

    def test_commands_that_are_not_a_commit_pass(self):
        self.standard_work()
        for command in ("git status --short", "git log --grep commit -3", "npm test", "git diff --stat"):
            self.assertEqual(self.before_commit(command), (0, ""), command)

    def test_other_tools_pass(self):
        self.standard_work()
        payload = {"hook_event_name": "PreToolUse", "tool_name": "Write", "tool_input": {"file_path": "git commit"}}
        self.assertEqual(self.run_hook(payload), (0, ""))


if __name__ == "__main__":
    unittest.main()
