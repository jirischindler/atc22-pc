# USENIX ATC 2022 Scripts

This repository contains various scripts and utilities that aid in running the USENIX ATC 2022 conference program committee.

## Incomplete registrations

To compile a list of submissions with incomplete registrations (empty or short abstract) follow the steps outlined below.

1. Download from HotCRP the CSV file with authors and titles (e.g., `atc22-authors.csv`)
2. Download the text of all abstracts (select Download "Text and abstracts" and save it as `all_data.txt`)
3. Run the `process_incomplete_submissions.py` script::
```sh
    # The directory <your_dir> is where you downloaded the HotCRP exported files
    python3 process_incomplete_submissions.py --dir <your_dir>
```

See the script's help for a complete list of options.
