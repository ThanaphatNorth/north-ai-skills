"""read_regular_file: bytes of a regular file; every other kind of path is an OSError, raised at once."""
import contextlib
import os
import shutil
import sys
import tempfile
import threading
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check import fileio  # noqa: E402
from ndev_check.fileio import HEAD_BYTES, read_regular_file, read_unless_head  # noqa: E402


@contextlib.contextmanager
def counted_reads():
    """Sizes of every read the check makes from a file: all of them pass through fileio's `os.read`."""
    real, sizes = os.read, []

    def read(fd, size):
        data = real(fd, size)
        sizes.append(len(data))
        return data

    with mock.patch.object(fileio.os, "read", read):
        yield sizes


def has_nul(head):
    return b"\0" in head


def lowest_free_descriptor():
    fd = os.open(os.devnull, os.O_RDONLY)
    os.close(fd)
    return fd


class ReadRegularFile(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="ndev-fileio-")
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)

    def path(self, name):
        return os.path.join(self.dir, name)

    def test_regular_file_and_symlink_to_one_give_the_bytes(self):
        with open(self.path("a.bin"), "wb") as fh:
            fh.write(b"caf\xe9\r\n\x00")
        os.symlink("a.bin", self.path("link"))
        self.assertEqual(read_regular_file(self.path("a.bin")), b"caf\xe9\r\n\x00")
        self.assertEqual(read_regular_file(self.path("link")), b"caf\xe9\r\n\x00")

    def test_missing_path_and_broken_symlink_are_file_not_found(self):
        os.symlink("nowhere", self.path("broken"))
        for name in ("absent", "broken"):
            with self.assertRaises(FileNotFoundError):
                read_regular_file(self.path(name))

    def test_directory_is_a_directory_error_and_leaves_no_descriptor_open(self):
        os.symlink(self.dir, self.path("to-dir"))
        before = lowest_free_descriptor()
        for name in ("", "to-dir", "", "to-dir"):
            with self.assertRaises(IsADirectoryError):
                read_regular_file(self.path(name))
        self.assertEqual(lowest_free_descriptor(), before)

    def test_fifo_is_an_error_at_once_and_leaves_no_descriptor_open(self):
        os.mkfifo(self.path("pipe"))
        before = lowest_free_descriptor()
        outcome = []

        def read():
            try:
                read_regular_file(self.path("pipe"))
            except OSError as err:
                outcome.append(err.strerror)

        reader = threading.Thread(target=read, daemon=True)
        reader.start()
        reader.join(10)
        self.assertEqual(outcome, ["not a regular file"], "blocked on the FIFO" if reader.is_alive() else "")
        self.assertEqual(lowest_free_descriptor(), before)

    def test_device_is_not_a_regular_file(self):
        with self.assertRaises(OSError) as ctx:
            read_regular_file(os.devnull)
        self.assertEqual((ctx.exception.strerror, ctx.exception.filename), ("not a regular file", os.devnull))


class ReadUnlessHead(unittest.TestCase):
    MEGABYTE = 1 << 20

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="ndev-fileio-")
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)

    def put(self, name, data):
        path = os.path.join(self.dir, name)
        with open(path, "wb") as fh:
            fh.write(data)
        return path

    def test_file_turned_down_by_its_head_is_not_read_any_further(self):
        """A video or a database dump: the megabyte behind the first 8 KB never enters memory."""
        path = self.put("clip.mp4", b"\x00\x00\x00\x18ftyp" + b"\xab" * self.MEGABYTE)
        with counted_reads() as sizes:
            self.assertIsNone(read_unless_head(path, has_nul))
        self.assertEqual(sum(sizes), HEAD_BYTES)

    def test_file_that_passes_is_read_whole_and_the_judge_sees_only_the_head(self):
        data = b"x = 1\n" * (self.MEGABYTE // 6) + b"\x00 a NUL far past the head\n"
        seen = []
        with counted_reads() as sizes:
            self.assertEqual(read_unless_head(self.put("big.py", data), lambda head: seen.append(head) or has_nul(head)),
                             data)
        self.assertEqual((seen, sum(sizes)), ([data[:HEAD_BYTES]], len(data)))

    def test_file_shorter_than_the_head_is_judged_whole(self):
        seen = []
        self.assertEqual(read_unless_head(self.put("tiny.py", b"x = 1\n"), lambda head: bool(seen.append(head))), b"x = 1\n")
        self.assertEqual(seen, [b"x = 1\n"])
        self.assertIsNone(read_unless_head(self.put("empty.bin", b""), lambda head: head == b""))

    def test_path_that_is_no_regular_file_raises_before_anything_is_judged(self):
        with self.assertRaises(IsADirectoryError):
            read_unless_head(self.dir, self.fail)
        with self.assertRaises(FileNotFoundError):
            read_unless_head(os.path.join(self.dir, "absent"), self.fail)

    def test_whole_file_reader_reads_every_byte_through_the_same_seam(self):
        data = os.urandom(3 * self.MEGABYTE + 17)
        with counted_reads() as sizes:
            self.assertEqual(read_regular_file(self.put("blob", data)), data)
        self.assertEqual(sum(sizes), len(data))


if __name__ == "__main__":
    unittest.main()
