#!/usr/bin/env python

"""
Convert bed files to JSON for display with a JQuery Datatable

"""
import os, sys
import traceback
from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter
import json
import contextlib


DEBUG = os.environ.get("BED2JSON_DEBUG", "FALSE").upper() == "TRUE"
__version__     = "0.5"
__date__        = "2018-04-16"
__updated__     = os.path.getmtime(__file__)


@contextlib.contextmanager
def stdopen(filename=None, mode="r"):
    if filename and filename != '-':
        fh = open(filename, mode)
    else:
        if mode == "w":
            fh = sys.stdout
        elif mode == "r":
            fh = sys.stdin
        else:
            raise Exception("Only handles r and w mode")
    try:
        yield fh
    finally:
        if fh is not sys.stdout and fh is not sys.stdin:
            fh.close()


def main():

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = "%%(prog)s %s (%s)" % (program_version, program_build_date)
    program_shortdesc = "bed2json -- Convert bed file to a JQuery Datatable-suitable JSON file."
    program_license = """%s

  Created by Aaron Kitzmiller on %s.
  Copyright 2018 The Presidents and Fellows of Harvard College. All rights reserved.

  Licensed under the GPL v2.0
  http://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
""" % (program_shortdesc, str(__date__))

    try:

        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-V", "--version", action="version", version=program_version_message)
        parser.add_argument("input", metavar="input", help="BED file", nargs='?')
        parser.add_argument("output", metavar="output", help="JSON file", nargs='?')

        # Process arguments
        args = parser.parse_args()
        data = []
        # headers = ["chr", "start", "end", "annotation"]

        with stdopen(args.input, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue
                fields = line.split("\t", 3)
                data.append(fields)

        if DEBUG:
            indent = 4
        else:
            indent = None

        with stdopen(args.output, "w") as f:
            f.write(json.dumps({"data" : data}, indent=indent))
            f.write("\n")

    except KeyboardInterrupt:
        return 0
    except Exception, e:
        if hasattr(e, "user_msg") and not DEBUG:
            sys.stderr.write(program_name + ": " + e.user_msg + "\n")
        else:
            sys.stderr.write(program_name + ": " + str(e) + "\n" + traceback.format_exc())
        sys.stderr.write("  for help use --help\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
