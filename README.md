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

#### Blocks

Blocks must be separated by at least one blank line in the CSV (i.e. 2
newlines.)

##### Block: Row 1

The first row of a block contains only one piece of information: the name of
the entity being represented, in singular form (for example, "sample")
contained in the first column. The other columns of the block's first row are
ignored, but can be used as column headers to make the design file more
human-readable.

A block's first (header) row may look like this:

<table>
<tr>
<td><strong>sample</strong></td><td>this is ignored</td><td>as is this</td><td>...</td>
</tr>
</table>

What this means is that the block in the design file represents a "sample",
i.e. one entry in the block's equivalent table in the database contains a
single sample's data.

The analyzer will include column headers in the first row in order to aid 
understanding and possibly allow easier modification of the analyzer output.

##### Block: Following Rows – Field Descriptions

The following series of rows in a design file block contain a list of field
descriptions, which are analogous to columns in a standard spreadsheet layout.
One database field is described for every one of these rows in the design file.

The generic format for a design file field description row is the following:

<table>
<tr>
<td>CSV Column Name</td>
<td>Database Field Name</td>
<td>Data Type</td>
<td>Nullable?</td>
<td>Null Values</td>
<td>Default</td>
<td>Description</td>
<td>Additional fields...</td>
</tr>
</table>

TODO


### Step 3: Database Generator

TODO


### Step 4: Testing

TODO


## Deploying the End Result

TODO
