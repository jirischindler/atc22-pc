import csv
import re

import logging
log = logging.getLogger()

# Returns a dictionary of authors and a count of papers.
# Paper number is the dictionary key and authors field
# is a list of a authors, each a dictionary.
def read_and_process_authors(filename):
    # paper,title,first,last,email,affiliation,country,iscontact
    authors = {}
    cnt = 0
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            paper = row['paper'].strip()
            if not paper in authors:
                authors[paper] = {
                    'title': row['title'],
                    'paper': paper,
                    'authors': [],
                }
                authors[paper]['authors'].append({
                    'first': row['first'],
                    'last': row['last'],
                    'email': row['email'],
                    'iscontact': row['iscontact'] == 'yes',
                })
                cnt += 1

    return authors, cnt


fields = [
            'Abstract',
            'Submission Type',
            'Operational Systems Track',
            'Changes since previous submission',
            'Previous work extension'
            'Differences from previous work',
            'Artifact Description',
            'Artifact Evaluation',
            'Topics',
            # put this as the last element to avoid confusion with "Submission Type"
            'Submission',
            ]

def read_and_process_all_data(filename):
    submregexp = re.compile('Submission \#(\d+):\s*(.*)')
    papers = {}
    cnt = 0
    submission = None
    key = None
    with open(filename, newline='') as f:
        for l in f.readlines():
            line = l.rstrip('\n')
            if line.startswith('==') or line.startswith('--'):
                continue
            found_key = False
            for field in fields:
                if field in line:
                    key = field
                    m = re.match(submregexp, line)
                    if m: # We found the "Submission" line
                        submission = m.group(1)
                        papers[submission] = {
                            field: m.group(2),
                        }
                    found_key = True
                    break
            if found_key:
                continue
            if submission is not None and key is not None:
                try:
                    if len(line) > 0:
                        papers[submission][key] += ' '
                    papers[submission][key] += line
                except KeyError:
                    papers[submission][key] = line            
    return papers

def find_authors(authors, title):
    # compare only the first 30 characters
    maxlen = 30
    for s in authors.keys():
        if len(title) < maxlen:
            maxlen = len(title)
        if authors[s]['title'][:maxlen] == title[:maxlen]:
            return authors[s], s
    return None, None
