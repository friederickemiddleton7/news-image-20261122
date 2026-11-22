#!/usr/bin/env python3
"""Grader entrypoint for news-image-20261122.

Shipped picture: entry.png sits next to this script, produced by make_image.py
at build time. A grading run only has to put those bytes where the harness
looks, so there is no imaging library, no font lookup and no network involved.

Two runs in fresh containers therefore emit byte-identical files.
"""

import os
import shutil
import sys

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_MIN_BYTES = 4096          # smaller than this cannot be a 1024x1024 page
FILENAME = "entry.png"


def say(message):
    print("news-image-20261122: " + message)


def fail(message):
    sys.stderr.write("news-image-20261122: ERROR " + message + "\n")
    raise SystemExit(1)


def source_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, FILENAME)


def target_dir():
    chosen = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return os.path.abspath(chosen)


def check_source(path):
    if not os.path.exists(path):
        fail("cannot find %s; clone the repository with its committed entry.png" % path)
    if not os.path.isfile(path):
        fail("%s exists but is not a regular file" % path)
    size = os.path.getsize(path)
    if size < PNG_MIN_BYTES:
        fail("%s holds only %d bytes; the image looks truncated" % (path, size))
    with open(path, "rb") as fh:
        head = fh.read(len(PNG_SIGNATURE))
    if head != PNG_SIGNATURE:
        fail("%s does not start with a PNG signature" % path)
    return size


def publish(src, size, dest_dir):
    try:
        os.makedirs(dest_dir, exist_ok=True)
    except OSError as exc:
        fail("output directory %s unusable (%s)" % (dest_dir, exc))

    dest = os.path.join(dest_dir, FILENAME)
    try:
        shutil.copyfile(src, dest)
    except OSError as exc:
        fail("could not write %s (%s)" % (dest, exc))

    landed = os.path.getsize(dest)
    if landed != size:
        fail("short copy at %s: %d of %d bytes" % (dest, landed, size))
    return dest


def main():
    src = source_path()
    size = check_source(src)
    dest = publish(src, size, target_dir())
    say("wrote %d bytes to %s" % (size, dest))


if __name__ == "__main__":
    main()
