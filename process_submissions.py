import os
import pathlib

import hotcrp_utils as hotcrp

import logging

log = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(message)s')

# The input CSV file (obtained as a sheet from the Google Sheets document)
authors_input_filename = "atc22-authors.csv"

data_input_filename = "all_data.txt"
data_input_filename = "sample_data.txt"

if __name__ == "__main__":
    script = os.path.realpath(__file__)
    path = os.path.dirname(script)

    path = os.path.join(str(pathlib.Path.home()), "Downloads")
    f = os.path.join(path, authors_input_filename)

    authors, cnt = hotcrp.read_and_process_authors(filename=f)
    log.info("Read all {} entries from CSV file {}".format(cnt, f))

#    for p in authors.keys():
#        print(authors[p])

    f = os.path.join(path, data_input_filename)

    papers = hotcrp.read_and_process_all_data(f)
    log.info("Read all data from CSV file {}".format(f))
#    print(papers['1'])

    for p in papers.keys():
        try:
            abstract = papers[p]['Abstract']
        except KeyError:
            # no abstract found
            abstract = ''
        if len(abstract) < 100:
            log.warning("Short abstract in paper {}".format(p))
            print("ABSTRACT: " + abstract)
            a = None
            try:
                a = authors[p]
                # a, submission = hotcrp.find_authors(authors, papers[p]['Submission'])
                print("<a href=\"https://atc22.usenix.hotcrp.com/paper/{}\">#{}: {}</a>".format(p, p, a['title']))
                print(a['authors'])
            except KeyError:
                pass
    print("DONE")
