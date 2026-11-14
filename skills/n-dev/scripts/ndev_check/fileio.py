"""Read a path only when it is a regular file. The one place the check opens a path it was handed, so a
FIFO, a socket or a device behind that path can never block the check or feed it without end."""
from __future__ import annotations

import contextlib
import errno
import os
import stat
from typing import Callable, Iterator, List, Optional

HEAD_BYTES = 8192       # how much of a file `read_unless_head` shows its caller before reading the rest
_CHUNK = 1 << 20


def read_regular_file(path: str) -> bytes:
    """The file's bytes. Raises the OSError `open` would (missing, no permission, a symlink loop), an
    IsADirectoryError for a directory on every platform, and an OSError "not a regular file" for the rest."""
    with _regular(path) as fd:
        return _read(fd)


def read_unless_head(path: str, rejects: Callable[[bytes], bool]) -> Optional[bytes]:
    """The file's bytes, or None when `rejects` turns down its first HEAD_BYTES: the rest of such a file
    (a video, a database dump) is never read. Raises as `read_regular_file` does."""
    with _regular(path) as fd:
        head = _read(fd, HEAD_BYTES)
        return None if rejects(head) else head + _read(fd)


@contextlib.contextmanager
def _regular(path: str) -> Iterator[int]:
    """A descriptor on the path, open for the length of the block and only for a regular file."""
    # O_NONBLOCK: opening a FIFO nobody writes to returns at once instead of waiting for a writer.
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0))
    try:
        mode = os.fstat(fd).st_mode
        if stat.S_ISDIR(mode):
            raise IsADirectoryError(errno.EISDIR, os.strerror(errno.EISDIR), path)
        if not stat.S_ISREG(mode):
            raise OSError(errno.EINVAL, "not a regular file", path)
        yield fd
    finally:
        os.close(fd)


def _read(fd: int, limit: Optional[int] = None) -> bytes:
    """Up to `limit` bytes from the descriptor, or all that is left. Every byte the check takes from a
    file passes through the `os.read` here."""
    chunks: List[bytes] = []
    left = limit
    while left is None or left > 0:
        chunk = os.read(fd, _CHUNK if left is None else min(left, _CHUNK))
        if not chunk:
            break
        chunks.append(chunk)
        left = None if left is None else left - len(chunk)
    return b"".join(chunks)
