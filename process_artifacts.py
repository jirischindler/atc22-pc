import argparse
import json
import os
import re
import sys

import hotcrp_utils as hotcrp

import logging

log = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)s - %(message)s')

data_input_filename = "atc22-data.json"

def process_artifacts(papers):
    #    "changes_since_previous_submission": " Described the testbed's software ..."
    #    "previous_work_extension": "No",
    #    "artifact_description": "We build a testbed for edge devices to evaluate the performance of ",
    #    "artifact_evaluation": "An artifact will be submitted for evaluation, if the paper is accepted.",
    no_re = re.compile('no artifact will be', re.IGNORECASE)
    will_be_avail_re = re.compile('An artifact will be (made)?(.*)(available|submitted)', re.IGNORECASE)
    is_available_re = re.compile('An artifact is(.*)available', re.IGNORECASE)
    artifacts = {}
    has_artifacts = []
    no_artifacts = []
    other_artifacts = []
    empty_artifacts = []
    for p in papers:
        pid = p['pid']
        try:
            aeval = p['artifact_evaluation'].lower()
        except KeyError:
            no_artifacts.append(pid)
            empty_artifacts.append(pid)
            artifacts[pid] = 'empty'
            continue
        if no_re.search(aeval):
            no_artifacts.append(pid)
            artifacts[pid] = 'no'
            continue
        if will_be_avail_re.search(aeval):
            has_artifacts.append(p['pid'])
            artifacts[pid] = 'yes'
            continue
        if is_available_re.search(aeval):
            has_artifacts.append(pid)
            artifacts[pid] = 'available'
            continue        
        other_artifacts.append(pid)

    log.info("Found {} papers with artifacts, {:.0f}%".format(
        len(has_artifacts),
#        " ".join(str(i) for i in has_artifacts)
        len(has_artifacts) / len(papers) * 100,
    ))
    log.info("Found {} papers without artifacts: , {:.0f}%".format(
        len(no_artifacts),
#         " ".join(str(i) for i in no_artifacts)
        len(no_artifacts) / len(papers) * 100,
    ))
    log.info("Found {} papers with empty artifact description: {:.0f}%".format(
        len(empty_artifacts), 
#         " ".join(str(i) for i in no_artifacts)
        len(empty_artifacts) / len(papers) * 100,
    ))
    print("Papers with artifacts: " + " ".join(str(i) for i in has_artifacts))
    print("")
    print("Papers w/o artifacts: " + " ".join(str(i) for i in no_artifacts))
    print("")
    print("Other papers: " + " ".join(str(i) for i in other_artifacts))    
    return artifacts


def handle_args():
    parser = argparse.ArgumentParser(description='Determine incomplete submissions',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--data', required=False, dest='json_file',
                        default=data_input_filename,
                        help='The JSON file with exported data')

    return vars(parser.parse_args())


if __name__ == '__main__':
    args = handle_args()

   #
    # Preparation: read the JSON file and make the destination directory.
    #
    try:
        paper_file = open(args['json_file'], encoding = 'latin-1')
    except (FileNotFoundError, PermissionError) as e:
        log.error('Failed to read input file: '+ str(e))
        sys.exit(1)
    papers = json.load(paper_file)

    artifacts = process_artifacts(papers)
