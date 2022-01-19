import argparse
import os
import sys

import hotcrp_utils as hotcrp

import logging

log = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)s - %(message)s')

# PC assignments
assignments_input_filename = "atc22-pcassignments.csv"

# data_input_filename = "sample_data.txt"
conflicts_input_filename = "atc22-pcconflicts.csv"

conflicts_in_assignemt_output_filename = "assigned_conflicts.csv"

def find_short_abstracts(papers, cutoff):
    dubious = []
    for p in papers.keys():
        try:
            abstract = papers[p]['Abstract']
        except KeyError:
            # no abstract found
            abstract = ''
        if len(abstract) < cutoff :
            log.warning("Short abstract in paper {}".format(p))
            dubious.append(p)
    return dubious


def handle_args():
    parser = argparse.ArgumentParser(description='Check for conflicts in assignments',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--dir', required=False, dest='dir', default=os.path.dirname(os.path.realpath(__file__)),
                        help='The directory prefix for files')
    parser.add_argument('--assignments-file',required=False, dest='assignments_filename', default=assignments_input_filename,
                        help='The CSV file with exported review assignments')
    parser.add_argument('--conficts-file', required=False, dest='conflicts_filename', default=conflicts_input_filename,
                        help='The CSV file with conflicts')

    return vars(parser.parse_args())


if __name__ == '__main__':
    args = handle_args()

    fname = os.path.join(args['dir'], args['assignments_filename'])
    assignments = hotcrp.read_and_process_review_assignments(fname)
    log.info("Read assignments data from CSV file {}".format(fname))

    fname = os.path.join(args['dir'], args['conflicts_filename'])
    all_conflicts, sorted_full_pc = hotcrp.read_and_process_conflicts(fname)
    log.info("Read PC conflicts data from CSV file {}".format(fname))

    for  pc in sorted_full_pc.keys():
        conflicts = set(all_conflicts[pc])
        assigned = set(assignments[pc])
        print("{}: {}".format(sorted_full_pc[pc], pc))

    sys.exit(0)

    f =  open(conflicts_in_assignemt_output_filename, 'w')
    emails = []
    for p in dubious: 
        try:
            abstract = papers[p]['Abstract']
        except KeyError:
            # no abstract found
            abstract = ''

        f.write("ABSTRACT: " + abstract + "\n")
        a = None
        try:
            a = authors[p]
            # a, submission = hotcrp.find_authors(authors, papers[p]['Submission'])
            f.write("<a href=\"https://atc22.usenix.hotcrp.com/paper/{}\">#{}: {}</a>\n\n".format(p, p, a['title']))
            for author in a['authors']:
                if author['iscontact']:
                    emails.append(author['email'])
            f.write("\n")
        except KeyError:
            pass
    f.close()
    log.info("Wrote incomplete abstacts details to {}".format(incomplete_output_filename))
