import csv
import operator

import logging
log = logging.getLogger()

fieldnames = ["email", "first", "last", "affiliation", "country", "level", "roles"]

def assign_level(resp):
    if "ight" in resp:
        return "light"
    return "heavy"

def read_and_process_members_list(filename):
    members = {}
    cnt = 0
    with open(filename, newline='') as csvfile:
        # Round,Invitation Date,Invited by,Response,Reponse Date,Reminder sent,Name,Affiliation,email,preferred email ,alternate email,Expertise,Previous ATC?,Early Career?,Industry / Academia,Country,Man/Woman,Minority,Website,Prev Heavy/Light

        reader = csv.DictReader(csvfile)
        for row in reader:
            resp = row['Response']
            name = row['Name'].strip()
            if not 'ccepted' in resp:
                # print("Declined " + name)
                continue
            level = assign_level(resp)
            affiliation = row['Affiliation'].strip()
            country = row['Country']
            n = name.split()
            if len(n) > 2:
                log.warn("Unusual name " + name)
                first = n[0]
                last = n[1:]
                log.info("Update to first: {}, last: {}".format(first,last))
            email = row['Email'].strip()
            members[email] = {
                "email": email,
                "first": n[0],
                "last": n[1],
                "affiliation": affiliation,
                "country": country,
                "level": level,
                "roles": "pc"
            }
            cnt += 1
    log.info("Processed {} names".format(cnt))
    return members


def write_members(filename, members):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

#        dict(sorted(members.items(), key=lambda item: item[1]))
        
        for k in members:
            writer.writerow(members[k])
