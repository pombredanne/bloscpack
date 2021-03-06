#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

import os.path as path
import os
import sys
import time
import subprocess
import bloscpack
import test_bloscpack as tb

DROP_CACHES = False


def get_fs(file_name):
    return bloscpack.pretty_size(path.getsize(file_name))


def get_ratio(file1, file2):
    return path.getsize(file1)/path.getsize(file2)


def drop_caches():
    if DROP_CACHES:
        os.system('echo 3 > /proc/sys/vm/drop_caches')


def am_root():
    return os.geteuid() == 0


if len(sys.argv) == 2 and sys.argv[1] in ('-d', '--drop-caches'):
    if am_root():
        print('will drop caches')
        DROP_CACHES = True
    else:
        print('error: need uid 0 (root) to drop caches')
        sys.exit(1)

with tb.create_tmp_files() as (tdir, in_file, out_file, dcmp_file):
    gz_out_file = path.join(tdir, 'file.gz')

    print('create the test data', end='')

    def progress(i):
        if i % 10 == 0:
            print('.', end='')
        sys.stdout.flush()
    tb.create_array(100, in_file, progress=progress)
    print('')

    print("Input file size: %s" % get_fs(in_file))
    drop_caches()

    print("Will now run bloscpack... ")
    tic = time.time()
    bloscpack.pack_file(in_file, out_file)
    toc = time.time()
    print("Time: %.2f seconds" % (toc - tic))
    print("Output file size: %s" % get_fs(out_file))
    print("Ratio: %.2f" % get_ratio(out_file, in_file))
    drop_caches()

    print("Will now run gzip... ")
    tic = time.time()
    subprocess.call('gzip -c %s > %s' % (in_file, gz_out_file), shell=True)
    toc = time.time()
    print("Time: %.2f seconds" % (toc - tic))
    print("Output file size: %s" % get_fs(gz_out_file))
    print("Ratio: %.2f" % get_ratio(gz_out_file, in_file))
