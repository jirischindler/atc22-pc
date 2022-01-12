#!/usr/bin/python3
#
# Tool for stamping HotCRP submissions with extra information.
#  Depends on pdftk, pdfinfo, and pdflatex with the geometry and
#  fancyhdr packages.
#
#
# BUGS:
#
# Error handling is primitive; on LaTeX errors the program will exit
# with an exception and leave the LaTeX log in "stamp.log".  On pdftk
# errors the program will exit with an exception and it'll be up to
# you to figure out why.
#
# Only supports letter and a4 paper.
#

"""Stamp HotCRP submissions to add useful information: the paper
number, an indication of tags, and page numbers.  Depends on pdflatex
with the geometry and fancyhdr packages, and on the pdftk tool.

To use this tool, first go to the HotCRP papers page and choose
"Download: JSON" at the bottom.  Save the JSON in a convenient place,
cd to the directory containing the paper, and then run the tool.
Stamped papers will be left in a "stamped" subdirectory.

Usage:
    stamp_papers [-d DIR] [-m MARGIN] [-t TAGS] [-p PAPERS] [-v] BASE JSON-FILE

BASE is the name of the conference that HotCRP prepends to paper
names.  For example, if papers are named "fast17-paper2.pdf" etc.,
then BASE is "fast17".

Options:
  -d DIR        Specify the directory in which to leave the papers.
                WARNING:  do not specify "."; doing so will clobber
                your papers.
                [Default: stamped]
  -m MARGINS    Specify the margins to assume on the paper, in LaTeX
                notation.  If one number is given, it applies to all
                margins.  Two comma-separated numbers are interpreted
                as left/right,top/bottom.  Four are interpreted as
                left,right,top,bottom.  [Default: 1in]
  -p PAPERS     Specify a comma-separated list of paper numbers to process.
                The default is to do all papers listed in the JSON file.
  -t TAGS       Specify a comma-separated list of tags to be considered
                when stamping papers.  Order matters.  For
                convenience, "-paper" may be left off the tag names.
                The default is to stamp papers with all tags.
  -v            Verbose: give some status as work is being done.

By default, the paper is marked with all tags given by HotCRP in the
"options" field (check boxes on the submissions form).  The -t option
can be used to choose specific desired tags; others are ignored.

Example:

    stamp_papers -t short-paper,student -p 2,4 -v fast17 fast17-data.json
"""

import docopt
import json
import os
import subprocess
import sys

LATEX_HEADER=r"""\documentclass[{size}paper]{{article}}
\usepackage[lmargin={lmargin},rmargin={rmargin},tmargin={tmargin},bmargin={bmargin}]{{geometry}}
\usepackage{{fancyhdr}}

\pagestyle{{fancy}}

\fancyhead{{}}
\renewcommand{{\headrule}}{{}}
\cfoot{{}}
\rfoot{{Page \thepage}}
"""

def main():
    arguments = docopt.docopt(__doc__, version = 'stamp_papers 1.0')
    if arguments['-d'] == '.':
        sys.stderr.write("Can't use '.' as destination directory\n")
        sys.exit(2)
    base = arguments['BASE']
    tags = arguments['-t'].split(',')
    if tags == ['']:
        tags = []
    margins = arguments['-m'].split(',')
    if len(margins) == 1:
        margins = [margins[0] for i in range(4)]
    elif len(margins) == 2:
        margins = [margins[0], margins[0], margins[1], margins[1]]
    elif len(margins) != 4:
        sys.stderr.write("Illegal margins specified\n")
        sys.exit(2)
    #
    # Preparation: read the JSON file and make the destination directory.
    #
    try:
        paper_file = open(arguments['JSON-FILE'], encoding = 'latin-1')
    except (FileNotFoundError, PermissionError) as e:
        sys.stderr.write("{}: {}\n".format(arguments['JSON-FILE'], e.strerror))
        sys.exit(1)
    papers = json.load(paper_file)
    if arguments['-p']:
        todo = [int(paper) for paper in arguments['-p'].split(',')]
        papers = [paper for paper in papers if paper['pid'] in todo]
    subprocess.call(["mkdir", "-p", arguments['-d']])
    for paper in papers:
        if arguments['-v']:
            print("Processing paper", paper['pid'])
        #
        # Get information about the paper.
        #
        output = subprocess.check_output(["pdfinfo",
          "{}-paper{}.pdf".format(base, paper['pid'])])
        output = output.decode('ascii', errors = 'ignore')
        output = output.split('\n')
        info_dict = {}
        for line in output:
            line = line.split(':', 1)
            if len(line) == 2:
                line = [i.strip() for i in line]
                info_dict[line[0]] = line[1]
        #
        # Create custom LaTeX source
        #
        stamp_source = open('stamp.tex', 'w')
        if 'a4' in info_dict['Page size'].lower():
            paper_size = 'a4'
        else:
            paper_size = 'letter'
        stamp_source.write(LATEX_HEADER.format(size = paper_size,
          lmargin = margins[0], rmargin = margins[1],
          tmargin = margins[2], bmargin = margins[3]))
        if tags == []:
            footer = [tag for tag in paper['options'].keys()
              if paper['options'][tag]]
        else:
            footer = [tag for tag in tags
              if tag in paper['options']  and  paper['options'][tag]
                or  tag + "-paper" in paper['options']
                  and  paper['options'][tag + "-paper"]]
        footer = [tag.replace("-paper", "").upper() for tag in footer]
        stamp_source.write('\\lfoot{{{} PAPER \\#{}}}\n\n' \
          .format(' '.join(footer), paper['pid']))
        stamp_source.write('\\begin{document}\n\n')
        for i in range(int(info_dict['Pages'])):
            stamp_source.write('~\n\\clearpage\n')
        stamp_source.write('\n\\end{document}\n')
        stamp_source.close()
        #
        # Run pdflatex to generate the stamp PDF.
        #
        result = subprocess.call(["pdflatex", "stamp.tex"],
          stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
        if result:
            raise subprocess.CalledProcessError(result, 'pdflatex')
        #
        # Use pdftk to apply the stamp.
        #
        result = subprocess.call(["pdftk",
            "{}-paper{}.pdf".format(base, paper['pid']),
            "multistamp", "stamp.pdf", "output",
            "{}/{}-paper{}.pdf".format(arguments['-d'], base, paper['pid'])])
        if result:
            raise subprocess.CalledProcessError(result, 'pdftk')
    #
    # Clean up
    #
    for ext in ['aux', 'log', 'pdf', 'tex']:
        os.unlink("stamp." + ext)

if __name__ == "__main__":
    main()
