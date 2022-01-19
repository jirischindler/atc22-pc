import argparse
import os
import sys

import hotcrp_utils as hotcrp

import logging

log = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)s - %(message)s')

# PC assignments
assignments_input_filename = "atc22-pcassignments.csv"

# Conflicts by paper
conflicts_input_filename = "atc22-pcconflicts.csv"

conflicts_in_assignment_output_filename = "assigned_conflicts.csv"

def handle_args():
    parser = argparse.ArgumentParser(description='Check for conflicts in assignments',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--dir', required=False, dest='dir', default=os.path.dirname(os.path.realpath(__file__)),
                        help='The directory prefix for files')
    parser.add_argument('--assignments',required=False, dest='assignments', default=assignments_input_filename,
                        help='The CSV file with exported review assignments')
    parser.add_argument('--conflicts', required=False, dest='conflicts', default=conflicts_input_filename,
                        help='The CSV file with conflicts')

    return vars(parser.parse_args())


if __name__ == '__main__':
    args = handle_args()

    fname = os.path.join(args['dir'], args['assignments'])
    assignments = hotcrp.read_and_process_review_assignments(fname)
    log.info("Read assignments data from CSV file {}".format(fname))

    fname = os.path.join(args['dir'], args['conflicts'])
    all_conflicts, sorted_full_pc = hotcrp.read_and_process_conflicts(fname)
    log.info("Read PC conflicts data from CSV file {}".format(fname))

    f =  open(conflicts_in_assignment_output_filename, 'w')
    cnt = 0
    for  pc in sorted_full_pc.keys():
        conflicts = set(all_conflicts[pc])
        try:
            assigned = set(assignments[pc])
        except KeyError:
            assigned = []
            log.warning("{} has no assignments".format(sorted_full_pc[pc]))

        # find the intersections of stated conflicts and assignments
        error_in_assignment = conflicts.intersection(assigned)

        # print("{}: {} {}".format(sorted_full_pc[pc], pc, conflicts))
        if len(error_in_assignment) > 0:
            log.error("{} has been assigned a conflicted paper(s): {}".format(sorted_full_pc[pc], error_in_assignment) )
            cnt += 1
    f.close()
    log.info("Wrote conflicts to {}".format(conflicts_in_assignment_output_filename))
    log.info("Found {} errors - conflicted PC assigned to a paper".format(cnt))
