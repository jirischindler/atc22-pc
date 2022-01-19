import argparse
import os
import sys

import hotcrp_utils as hotcrp

import logging

log = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)s - %(message)s')

# The input CSV file (obtained as a sheet from the Google Sheets document)
authors_input_filename = "atc22-authors.csv"

data_input_filename = "all_data.txt"
# data_input_filename = "sample_data.txt"

incomplete_output_filename = "incomplete-abstracts-stats.txt"

abstract_length_warning_cutoff = 75

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
    parser = argparse.ArgumentParser(description='Determine incomplete submissions',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--dir', required=False, dest='dir', default=os.path.dirname(os.path.realpath(__file__)),
                        help='The directory prefix for files')
    parser.add_argument('--authors-file',required=False, dest='authors_filename', default=authors_input_filename,
                        help='The CSV file with exported authors')
    parser.add_argument('--text-file', required=False, dest='text_filename', default=data_input_filename,
                        help='The text file with exported text and abstracts')
    parser.add_argument('--cutoff', required=False, dest='cutoff', default=abstract_length_warning_cutoff,
                        type=int,
                        help='The minimal length of abstract to consider the registration as complete')

    return vars(parser.parse_args())


if __name__ == '__main__':
    args = handle_args()

    fname = os.path.join(args['dir'], args['text_filename'])
    papers = hotcrp.read_and_process_all_data(fname)
    log.info("Read papers data from CSV file {}".format(fname))

    dubious = find_short_abstracts(papers, args['cutoff'])
    log.info("Found {} papers with short or incomplete abstract".format(len(dubious)))

    # Print out submission numbers with incomplete abstacts
    print(" ".join(dubious))

    sys.exit(0)

    fname = os.path.join(args['dir'], args['authors_filename'])
    authors, cnt = hotcrp.read_and_process_authors(filename=fname)
    log.info("Read all {} entries from CSV file {}".format(cnt, fname))


    f =  open(incomplete_output_filename, 'w')
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


    # Print comma-separated emails of first authors with incomplete abstracts
    # Suitable for C&P into an email program.
#    print("EMAILS:")
#    print(','.join(emails))
#    print("\n")
