#!/usr/bin/env python
# Copyright (c) 2015 Scott Vokes <vokes.s@gmail.com>
# 
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

DESCR = """
A Python implementation of the Burrows-Wheeler Transform
for my !!Con 2015 talk, "The Burrows-Wheeler Transform:
Better Compression with a Reversible Sort!!".
"""

def bwt(s, verbose=False):
    """Apply the Burrows-Wheeler Transform to a string, s.
    Return the transformed text and starting offset."""
    if len(s) < 2:
        # nothing to do
        return s, 0

    # text -> list of offsets
    idx = [i for i in range(len(s))]

    # sort slices, wrapping
    def cmp_rot(a, b):
        return cmp(s[a:] + s[:a],
                   s[b:] + s[:b])

    if verbose:
        rs = [s[i:] + s[:i] for i in range(len(s))]
        for r in rs:
            print(r)

    idx.sort(cmp_rot)

    # find starting offset
    start = idx.index(1)

    if verbose:
        print("\n%s\n" % (idx))
        for i in idx:
            print(s[i:] + s[:i])

    # return last column & start pos
    return (''.join([s[i - 1] for i in idx]),
            start)    

def unbwt(s, start, verbose=False):
    """Invert the Burrows-Wheeler Transform on a string, s,
    with a known starting offset. Returns the original string."""
    # nothing to do
    if len(s) < 2: return s

    # count letter occurrences
    seen = {}
    def enumerate(c):
        i = seen.get(c, 1)
        seen[c] = i + 1
        return (c, i)

    # pair up (last, first) columns
    l = [enumerate(c) for c in s]
    f = l[:]
    f.sort()
    pairs = zip(l, f)

    # wrap current row's last
    # column to find next row
    def find(v):
        for r in pairs:
            if r[0] == v:
                return r
    # (linear search)

    if verbose:
        for i in range(len(pairs)):
            r = pairs[i]
            m = (i == start and "*" or "")
            print("    %s %d <---> %s %d %s" %
                  (r[1][0], r[1][1], r[0][0], r[0][1], m))

    res = []
    # start at beginning row
    row = pairs[start]

    # save row's letter, find next row
    for i in range(len(s)):
        res.append(row[0][0])
        row = find(row[1])

    return ''.join(res)


def repl(verbose=False):
    while True:
        import sys
        sys.stdout.write("text> ")
        s = sys.stdin.readline()
        if s == None or len(s) <= 1:
            break
        elif s[-1] == '\n':
            s = s[:-1]

        transformed, offset = bwt(s, verbose)
        print("\n%s\n%s^\n" % (transformed, " " * offset))
        back = unbwt(transformed, offset, verbose)
        print("%s\n" % (back))
        assert back == s

def test(verbose=False, ceil=100):
    import random
    import time

    def test_case(s, verbose=False):
        transformed, offset = bwt(s, verbose)
        back = unbwt(transformed, offset, verbose)
        assert back == s

    def randstr(length, seed=time.time()):
        random.seed(seed)
        return ''.join([chr(random.randint(32, 127)) for x in range(length)])

    for i in range(ceil):
        test_case(randstr(i, i), verbose)
        test_case(("aaaaaaaaab" * (i/10)) + ("a" * (i % 10)), verbose)

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=DESCR)
    p.add_argument("-t", "--test", action="store_true", help="Run fuzz tests.")
    p.add_argument("-v", "--verbose", action="store_true", help="Show intermediate steps.")
    p.add_argument("-r", "--repl", action="store_true", help="Run a REPL.")
    args = p.parse_args()

    if args.test:
        test(args.verbose)

    if args.repl:
        repl(args.verbose)

    if not args.test and not args.repl:
        p.print_help()
