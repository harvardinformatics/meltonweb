#!/usr/bin/env python

"""
Convert bed files to JSON for display with a JQuery Datatable

"""
import os, sys
import traceback
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import contextlib


DEBUG = os.environ.get("BED2JSON_DEBUG", "FALSE").upper() == "TRUE"
__version__     = "0.5"
__date__        = "2018-04-16"
__updated__     = os.path.getmtime(__file__)


HTMLTEMPLATE = """
<html>
    <head>
       <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.16/css/dataTables.bootstrap4.min.css"/>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/responsive/2.2.1/css/responsive.bootstrap4.min.css"/>
        <link rel="stylesheet" type="text/css" href="style.css"/>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
        <script type="text/javascript" src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
        <script type="text/javascript" src="https://cdn.datatables.net/1.10.16/js/jquery.dataTables.min.js"></script>
        <script type="text/javascript" src="https://cdn.datatables.net/1.10.16/js/dataTables.bootstrap4.min.js"></script>
        <script type="text/javascript">
            $(document).ready(function(){{
                $("#datatable").DataTable( {{
                    pageLength: 5000,
                    dom:        "pftp",
                }} );
             }});
        </script>
    </head>
    <body>
        <div>
            <div class="main_container">
                <div class="row">
                    <div class="col-md-12 col-sm-12 col-xs-12">
                        <div class="x_panel">
                            <div class="x_title">
                                <h2>Melton lab stuff</h2>
                                <div class="clearfix"></div>
                            </div>
                            <div class="x_content" style="width: 100%">
                                <table id="datatable">
                                    <thead>
                                        <th>Chromosome</th>
                                        <th>Start</th>
                                        <th>End</th>
                                        <th>ID</th>
                                        <th>closesst_NM_TS</th>
                                    </thead>
                                    <tbody>
                                        {tablebody}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
</html>
"""

ROWTEMPLATE = """
    <tr>
        <td>{chr}</td>
        <td>{start}</td>
        <td>{end}</td>
        <td>
            <a href="http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg19&position={chr}:{start}-{end}&hgt.customText=http://meltonlab.rc.fas.harvard.edu/data/UCSC/SCbetaCellDiff_ATAC_H3K4me1_H3K27ac_WGBS_tracks.txt">{ID}</a>
        </td>
        <td>{closesst_NM_TS}</td>
    </tr>
"""


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
    program_shortdesc = "bed2html -- Convert bed file to a html for Melton Lab web page."
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
        parser.add_argument("output", metavar="output", help="HTML file", nargs='?')

        # Process arguments
        args = parser.parse_args()
        data = []
        # headers = ["chr", "start", "end", "annotation"]

        with stdopen(args.input, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue
                fields = line.split("\t", 4)
                row = ROWTEMPLATE.format(chr=fields[0], start=fields[1], end=fields[2], ID=fields[3].replace("|", " | "), closesst_NM_TS=fields[4].replace("|", " | "))
                data.append(row)

        with stdopen(args.output, "w") as f:
            f.write(HTMLTEMPLATE.format(tablebody="\n".join(data)))
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
