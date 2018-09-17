# PyTrackDat

## Overview

**PLEASE NOTE THAT CURRENTLY PYTRACKDAT ONLY RUNS ON MAC OS AND LINUX.**

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
<td><strong>sample</strong></td>
<td>this is ignored</td>
<td>as is this</td>
<td>...</td>
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

Each of these columns in the field description row has specific acceptable
values which directly decide the resulting database structure. As such, it is
important to double-check these values if the automatic analyzer is used.

###### CSV Column Name

This cell should correspond exactly to the column name in the original data CSV
which stores data for field being described.

###### Database Field Name

This cell contains the name of the field as it will appear in the database.
It should only contain lowercase characters, numbers, and underscores.

###### Data Type

This cell contains the data type of the field in question. It can be one of the
following values:

```
auto key
manual key
foreign key
integer
float
decimal
boolean
text
date
time
```

This dictates what values can be stored in the field in the database. In
general, databases are much more strict (as compared to spreadsheet programs
such as Excel) with data typing, which prevents incorrect data values from
being entered and allows additional operations on types that allow them (such
as the addition of integers.)

For a more comprehensive overview on why data types are benificial when it
comes to data entry and integrity, see [tutorial.md](tutorial.md).

For a description of which values are acceptable for each data type, see the
"Data Type Descriptions" section below.

###### Nullable?

This cell contains a boolean (true or false) value which specifies whether the
value of the field in the database can be `NULL`. If the field contains any
value other than "true", "false" is inferred. Null is a special value which has
implications on data representation; for more information see
[tutorial.md](tutorial.md).

###### Null Values

This cell contains a semicolon-separated list (`;`, optionally with surrounding
spaces to make the cell contents more readable) of values in the data CSV file
which will be converted to a `NULL` value in the database. 

Note that if this cell contains multiple entries, **information is being
lost**, since multiple values in the original data are mapped to a single value
in the database, therefore preventing the original data from being recovered in
identically.

An example of where multiple values could be useful is the following:

```NA; N/A```

In this case, these two values mean the same thing to a human reader but are
completely different to the computer. If `NA` is, for example, the only
possible non-integer value in an integer field, it would make sense to map it
to `NULL`.

###### Default

This cell contains a value, of the same type as would appear in the data CSV
file, specifying the default value for the field in the database.

TODO: WHERE IS THIS ACTUALLY USED???

###### Description

This cell should contain a succinct and comprehensive description of what the
field means in the context of the dataset the database is to contain, including
explanations of possible values if non-obvious. 

It is also used to display help text below the fields in the database
single-item entry GUI.

###### Type-Specific Settings

Any cell after the description cell is type-specific and the valid values
depend on what data type the field has. There can be more than one
type-specific setting available, and the exact number also depends on the
field's type. For a description of each data type, including type-specific
setting options, see the section below.

#### Data Type Descriptions

TODO: With additional field descriptions

##### `auto key`: Automatic Primary Key

Automatic primary key (identifier) for a database row; stored as an integer
which starts at 1 and is increased by 1 for every row added to a table.

Deletion of a row does not lead to re-assigning IDs above the now-deleted row's
ID; IDs are fixed as long as the database is not completely re-created.

###### Design File Information

The following design file cells are **ignored** for `auto key`:

```
CSV Column Name, Nullable, Null Values, Default
```

Automatic primary keys are **never** nullable.

###### Type-Specific Settings

**No** type-specific settings are available for `auto key`.

##### `manual key`: Manually-Specified Primary Key

Manually-specified primary key (identifier) for a database row; stored as text.
The value must be specified by the user when adding data to the database.

Manually-specified primary keys must be **unique** for a given row.

###### Design File Information

The following design file cells are **ignored** for `manual key`:

```
Nullable, Null Values, Default
```

Manually-specified primary keys are **never** nullable.

###### Type-Specific Settings

**No** type-specific settings are available for `manual key`.

##### `integer`: Integer (Negative or Positive Whole Number)

Integers can be between -9 223 372 036 854 775 808 and
9 223 372 036 854 775 807. If a bigger-capacity field is needed, use a
`text`-type field instead.

###### Type-Specific Settings

TODO

##### `float`: Floating Point Number (Non-Fixed Precision Decimal)

Floating-point numbers can store a huge range of numbers, including numbers
with decimal points. However, there are precision issues, and
**whenever possible** the `decimal` type should be used instead to prevent
floating-point-specific errors (see [tutorial.md](tutorial.md).) 

###### Type-Specific Settings

TODO

##### `decimal`: Fixed-Precision Decimal Number

Decimal-typed numbers can store fixed-precision decimal numbers. Both the
overall maximum length and decimal precision must be specified, in number of
digits. This type is useful for encoding significant figures and **avoiding**
floating-point-specific errors (see [tutorial.md](tutorial.md).)

###### Type-Specific Settings

The `decimal` type requires two type-specific settings:

  1. `max length`: The maximum length a number can be, in digits; includes the
     decimal portion of the number.
  1. `precision`: The number of digits after the decimal. Will be the same for
     any value stored in the database, with the end 0-padded if necessary.

For example, a `decimal` field with a `max length` of 10 and a `precision` of 4
can store numbers such as `50.2300` or `-999999.9999` or `999999.9999` (as a 
negative sign does not count as a digit) but **cannot** store `1000000.0000`.

##### `boolean`: Boolean (True or False) Value

Boolean values are either `true` or `false`. If the field is made nullable, an
additional option is added, `NULL` (or unknown). If more than 3 values are
needed (for example if there are two types of unknown values), a text field
with the `choices` setting should be used.

###### Type-Specific Settings

**No** type-specific settings are available for `boolean`.

##### `text`: Fixed- or Unbounded-Length Text

TODO

###### Type-Specific Settings

The `text` type optionally can take up two type-specific settings:

  1. `max length`: The maximum length of the contents in the field in terms of
     number of characters.
  1. `options`: A semicolon-separated list of possible values the text field
     can take on. Limiting the domain of a field can be useful in order to
     speed up data entry, prevent typos, and restrict the domain of a field to
     exactly what is desired.

##### `date`: Date (TODO: TIMEZONED??)

TODO

Currently, PyTrackDat only accepts the `YYYY-MM-DD` format for dates.

###### Type-Specific Settings

**No** type-specific settings are available for `date`.

##### `time`: Time (TODO: 24 hr probably, TIMEZONED?)

TODO

Currently, PyTrackDat only accepts the `HH:MM` or `HH:MM:SS` 24 hour formats 
for times.

###### Type-Specific Settings

**No** type-specific settings are available for `time`.

##### `foreign key`: Foreign Key (Cross-Relation)

Foreign keys are one of the most powerful features of relational databases, and
in fact are what make then "relational" at all. A foreign key is a field on one
table which refers to the **primary key** of a row in *another* table (and in
fact, can refer to another row in the *same* table as well.)

This lets rows refer to one another, and can be used to prevent data
duplication. Reducing data duplication is important in preventing contradictory
information in a dataset. 

###### Type-Specific Settings

The `foreign key` type requires one type-specific setting:

  1. `target`: The table which the foreign key field is pointing to. Remember
     that table names are specified in the first column of the first row of
     a block in the design file.


### Step 3: Database Generator

The core of PyTrackDat is a database generator script, which uses a provided
CSV design file (see above for the format) to generate a database along with a
web application which can be used to administer it. The generated software is
powered by the [Django framework](https://www.djangoproject.com/).

To run the database generator on a design file (ex. `design.csv`), run the
following command:

```bash
python3 ./generate.py design.csv site_name
```

Where `design.csv` is a path to the design file and `site_name` is the name of
the web application that will be generated.

This will output a zip file, `site_name.zip`, in the PyTrackDat project
directory. This package will be used to deploy the site.


### Step 4: Testing

To test the web application from the PyTrackDat directory, first move into the
site directory within the temporary work directory, `tmp`, which PyTrackDat
will create, replacing `site_name_here` with the site name from the previous
(generator) step:

```bash
cd tmp/site_name_here
```

Then, activate the Python virtual environment with the following command:

```bash
source env/bin/activate
```

Before starting the debug server, a **superuser** (administrative user) must
be created for the web application. This can be done by running the following
command and following the prompts which will appear onscreen:

```bash
./manage.py createsuperuser
```

Finally, run the development server from the command line with the following
command, and navigate to the application in your web browser at
`127.0.0.1:8000`:

```bash
./manage.py runserver
```

To stop the server, press `Ctrl-C` in the terminal window where the server is
running.


## Deploying the End Result

TODO
