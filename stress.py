#!/usr/bin/env python
from __future__ import print_function
from multiprocessing import Pool
from multiprocessing import cpu_count
from contextlib import contextmanager
import signal
import argparse
import sys
import subprocess
import re
import signal


shouldRun = True
pool = None

def exit_gracefully(sig, frame):
    print("Tests will stop")
    shouldRun = False
    if pool is not None:
        pool.terminate()
    sys.exit(0)


def load(x):
    while shouldRun:
        x*x


@contextmanager
def start_test(options, command, prog_args):
    call = [command]
    call.extend(prog_args)
    print("Start testing. Will run %i times." % (options.repeat_count))

    fail_pattern = re.compile(options.grep_fail)
    success_pattern = re.compile(options.grep_success)

    for i in range(options.repeat_count):
        print("\n---------")
        print("Run %i" % (i+1))
        proc = subprocess.Popen(call, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        pid = proc.pid
        ret = proc.returncode
        shouldPrint = options.verbose
        failed = False

        if out is None:
            out = ""
        else:
            out = str(out)
        if err is None:
            err = ""
        else:
            err = str(err)

        print("Process ID was %i" % (pid))

        if ret == 0 and re.search(success_pattern, out) is not None:
            print("\033[30;42mSuccess\033[0m")
        elif ret == 0 and ((fail_pattern.search(out) is not None) or (fail_pattern.search(err) is not None)):
            print("\033[30;43mAssume fail. Return code is 0, but fail output\033[0m")
            shouldPrint = True
            failed = True
        elif ret == 0:
            print("\033[30;43mAssume success. Return code is 0, but no success output\033[0m")
        elif ret != 0 and ((fail_pattern.search(out) is not None) or (fail_pattern.search(err) is not None)):
            print("\033[30;41mFail\033[0m")
            shouldPrint = True
            failed = True
        elif ret != 0:
            print("\033[30;43mAssume fail. Return code is non-zero, but no fail output\033[0m")
            shouldPrint = True
            failed = True

        if shouldPrint:
            print(out)
            print(err, file=sys.stderr)

        print("~~~~~~~~~\n")

        if failed and options.stop_on_fail:
            break

    shouldRun = False
    print("Test finished")
    sys.stdout.write('\a')



def dispatch_stress():
    processes = cpu_count()
    pool = Pool(processes)
    pool.map_async(load, range(processes))
    pool.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Print all output from program")
    parser.add_argument("-s", "--stress", action="store_true", help="Load CPU")
    parser.add_argument("-n", "--repeat-count", type=int, help="Number of times to repeat", default=100)
    parser.add_argument("-x", "--stop-on-fail", help="Abort program execution on fail", action="store_true")
    parser.add_argument("-gf", "--grep-fail", type=str, help="Search for curtain fail RegExp in program output", default="[Ff][Aa][Ii][Ll]")
    parser.add_argument("-gs", "--grep-success", type=str, help="Search for curtain success RegExp in program output", default="([Pp][Aa][Ss][Ss])|([Ss][Uu][Cc][Cc][Ee][Ss][Ss])")
    parser.add_argument("command", help="Command to be run (with arguments)")
    args, _ = parser.parse_known_args()

    prog_args = sys.argv[sys.argv.index(args.command)+1:]

    signal.signal(signal.SIGINT, signal.SIG_IGN)

    if args.stress:
        dispatch_stress()

    signal.signal(signal.SIGINT, exit_gracefully)

    start_test(args, args.command, prog_args)

    if pool is not None:
        pool.terminate()

