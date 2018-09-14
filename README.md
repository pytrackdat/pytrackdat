# PyTrackDat

## Overview

TODO



## Installation

### Dependencies

First, make sure Python 3, `pip`, and `virtualenv` are installed.

TODO: More instructions on installing requirements


### Getting the Code

First, download the repository, either by using a packaged version from GitHub
or using the following `git` command:

```bash
git clone https://github.com/ColauttiLab/PyTrackDat.git
```

Once downloaded, un-archive it if needed. Then, open a terminal window and
`cd` to the directory PyTrackDat is stored in:

```bash
cd /path/to/pytrackdat
```

> **Beginner Tip**: TODO: Paths and stuff (using command line)



## Running PyTrackDat

### (Optional) Step 1: Data Analyzer

PyTrackDat includes an automatic data analyzer which can read a series of CSV
files in, as well as their desired relation names, and generate a PyTrackDat
**design file**, which contains human-readable CSV-formatted instructions for
the structure of the database.

To run the data analyzer on one or more CSV-formatted data files, run the
following command:

```bash
python3 ./analyze.py design.csv sample_type_1 samples1.csv sample_type_2 samples2.csv [...]
```

Where `design.csv` is the name of the design file to output, and
`sample_type_1` and `sample_type_2` are singular terms for the types of entries
stored in `samples1.csv` and `samples2.csv`, respectively. 


### Step 2: Design File Layout and Customization

A PyTrackDat design file contains specifications for all tables in the database
within a single CSV file. The file consists of 'blocks' which correspond to the
specification for a single table. Blocks are separated by blank lines.

A single block may look like this:

<table>
<tr>
    <th>my_sample</th>
    <th>new field name</th>
    <th>data type</th>
    <th>nullable?</th>
    <th>null values</th>
    <th>default</th>
    <th>description</th>
    <th colspan="2">additional fields...</th>
</tr>
<tr>
    <td></td>
    <td>sample_id</td>
    <td>auto key</td>
    <td></td>
    <td></td>
    <td></td>
    <td>Unique automatically-generated sample identifier.</td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>Date</td>
    <td>date</td>
    <td>integer</td>
    <td>false</td>
    <td></td>
    <td></td>
    <td>Date the sample was collected.</td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>Site ID</td>
    <td>site_id</td>
    <td>foreign key</td>
    <td>false</td>
    <td></td>
    <td></td>
    <td>Site where the sample was found.</td>
    <td></td>
    <td></td>
</tr>
<tr><td colspan="9">...</td></tr>
</table>

TODO

#### Design File Specification

TODO


### Step 3: Database Generator

TODO


### Step 4: Testing

TODO


## Deploying the End Result

TODO
