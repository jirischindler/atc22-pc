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
    regexp1 = re.compile('no artifact will be', re.IGNORECASE)
    regexp2 = re.compile('An artifact will be (made)?(.*)(available|submitted)', re.IGNORECASE)
    regexp3 = re.compile('An artifact is(.*)available', re.IGNORECASE)
    #    "changes_since_previous_submission": "- Described the testbed's software in more detail by using another image to give a better high-level overview of its working principle and functionality.\r\n- Described the used tools in more detail to allow an easier re-build by the reader.\r\n- Added experiments with a batch size of 10 to allow a better comparison of different batch sizes on the network and CPU load.\r\n- Added a new edge device configuration (Raspberry Pi with 4 GB of memory) to evaluate the difference in energy consumption under different settings between these two configurations.\r\n- Added a lessons learned chapter to give clear take-away messages for the reader.\r\n- Shorten the paper to be more on point and to remove redundant information to improve reading flow.\r\n- Added more up-to-date references for the related work chapter to incorporate the latest published research since the last submission.",
    #    "previous_work_extension": "No",
    #    "artifact_description": "We build a testbed for edge devices to evaluate the performance of Federated Learning algorithms. We designed a hardware and software stack consisting of the below mentioned parts to be scalable and flexible for different scenarios. The source code for conducting the experiments, the monitoring and the evaluation is made open-source.\r\n\r\nHardware platform: Raspberry Pi 4B\r\n\r\nSoftware: Ubuntu 20.04, PySyft v0.2.9, PostgreSQL 12.9, MQTT 2.0.14\r\n\r\nExperiments: Performance of Federated Learning algorithm under different emulated network conditions.\r\n",
    #    "artifact_evaluation": "An artifact will be submitted for evaluation, if the paper is accepted.",
    artifacts = {}
    has_artifacts = []
    no_artifacts = []
    other_artifacts = []
    for p in papers:
        pid = p['pid']
        try:
            aeval = p['artifact_evaluation'].lower()
        except KeyError:
            no_artifacts.append(pid)
            artifacts[pid] = 'empty'
            continue
        if regexp1.search(aeval) is not None:
            no_artifacts.append(pid)
            artifacts[pid] = 'no'
            continue
        if regexp2.search(aeval) is not None:
            has_artifacts.append(p['pid'])
            artifacts[pid] = 'yes'
            continue
        if regexp3.search(aeval) is not None:
            has_artifacts.append(pid)
            artifacts[pid] = 'available'
            continue        
        other_artifacts.append(pid)
    print(has_artifacts)
    print("\n")
    print("No artifacts " + " ".join(str(i) for i in no_artifacts))
    return artifacts


def handle_args():
    parser = argparse.ArgumentParser(description='Determine incomplete submissions',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--dir', required=False, dest='dir', default=os.path.dirname(os.path.realpath(__file__)),
                        help='The directory prefix for files')
    parser.add_argument('--data', required=False, dest='json_file', 
                        default='../hotcrp-downloaded/atc22-data/atc22-data.json',
                        # default=data_input_filename,
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
