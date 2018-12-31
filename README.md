# PyTrackDat

## Overview

PyTrackDat comprises a series of three Python scripts that analyze and assist 
in the conversion of data and relevant metadata from .csv files into an online
database that can facilitate data management, manipulation, and quality
control. What each of these does is outlined in the `README.md` file. Note that
the care that is taken to assemble `.csv` files before using these scripts will
help ensure that the database generated is maximally useful.



## Installation

### Dependencies

Make sure Python 3, `pip3`, `virtualenv`, and `wheel` are installed. The latter
two are Python packages, to be installed using `pip3`, the Python 3 package
manager.

If Python 3 is already installed, update `pip3` to the latest version with the
following command, ran in a Terminal window (macOS/Linux) or in Command Prompt
(Windows):

**macOS/Linux**:

```bash
pip3 install --upgrade pip
```

**Windows**:

```cmd
pip install --upgrade pip
```


#### Installing Python 3

For most new Linux distributions, Python 3 should come pre-installed.

For macOS or Windows, please go to the
[official Python website](https://www.python.org/downloads/)
and download the latest version of Python3 (as of the time of writing, 3.7.1).
Run the installer downloaded from this site and follow the instructions
on-screen.

##### Important: Special Windows Installation Instructions

When installing Python 3 on Windows, **make sure** to check the following
checkbox ("Add Python 3 to PATH"), which will appear on the first step of the
installation process:

<img src="images/path.png" alt="'Add Python 3.7 to PATH' checkbox" width="600">

This ensures that Python 3 and `pip` are available from the Command Prompt.


#### Installing `virtualenv` and `wheel`

To install `virtualenv` and `wheel`, a command must be ran in a Terminal window
(macOS or Linux), or a Command Prompt (on Windows). To open a Command Prompt,
press Windows Key + R or open the Start Menu, type in "cmd", and press enter.

Run the following command on **macOS** or **Linux**:

```bash
pip3 install virtualenv wheel
```

Run the following command on **Windows**:

```cmd
pip install virtualenv wheel
```


### Getting the Code

First, download the repository, either by using a packaged version from GitHub
or using the following `git` command:

```bash
git clone https://github.com/ColauttiLab/PyTrackDat.git
```

Once downloaded, un-archive it if needed. Then, open a Terminal window
(macOS/Linux) or a Command Prompt (Windows) and `cd` to the directory
PyTrackDat is stored in:

```bash
cd /path/to/pytrackdat
```



## Running PyTrackDat

### (Optional) Step 1: Data Analyzer

PyTrackDat includes an automatic data analyzer which can read a series of CSV
files in, as well as their desired relation names, and generate a PyTrackDat
**design file**, which contains human-readable CSV-formatted instructions for
the structure of the database. This design file is not final, and should be
checked over and filled out by a human. However, it provides a good starting
point for generating a database for a particular dataset.

To run the data analyzer on one or more CSV-formatted data files, run the
following command:

**macOS/Linux:**

```bash
python3 ./analyze.py design.csv sample_type_1 samples1.csv sample_type_2 samples2.csv [...]
```

**Windows**:

```cmd
python ./analyze.py design.csv sample_type_1 samples1.csv sample_type_2 samples2.csv [...]
```

Where `design.csv` is the name of the design file to output, and
`sample_type_1` and `sample_type_2` are singular terms for the types of entries
stored in `samples1.csv` and `samples2.csv`, respectively. 


### Step 2: Design File Layout and Customization

A PyTrackDat design file contains specifications for all tables in the database
within a single CSV file. The file consists of 'blocks' which correspond to the
specification for a single table, based on one of the CSV files passed to the
script. Blocks are separated by blank lines.

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

Design files should **not** be left as-is after generation via `analyze.py`.
The script does its best to infer data types from the columns, but is not
guaranteed to do a perfect job. Additionally, it is best practice to add a
**field description** (under the *description* header) in order to provide
human users additional information about what type of data is stored in the
field.

For each generated design file, users should examine the file using the
following checklist:

1. Check that data types and type-specific options are correct for each field
2. Add human-readable **descriptions** for each field
3. Change desired **foreign keys** from their detected data type to the foreign
   key data type, following the foreign key documentation (TODO: LINK) to link
   them to the correct table.
   
#### Design File Customization

In almost all cases, there are data types and settings that will be impossible
for the `analyze.py` script to detect. For example, a **foreign key**, which is
a data type that allows a row in a table to refer to a different row in either
the same table or a different table, cannot be automatically detected. Foreign
keys are very useful for reducing data duplication and encoding complex data
relationships.

In other cases, it may be desirable to limit a field to a range of data types.
For example, if a specimen can be one of four species, it is desirable to make
a text field which can only store any of these four species' names. The analyze
script does its best to detect these instances, but it may not detect
**all possible choices**. Thus, text fields with automatically-detected choice
limitations should be examined by hand.

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
comes to data entry and integrity, see [manual.md](manual.md).

For a description of which values are acceptable for each data type, see the
"Data Type Descriptions" section below.

###### Nullable?

This cell contains a boolean (true or false) value which specifies whether the
value of the field in the database can be `NULL`. If the field contains any
value other than "true", "false" is inferred. Null is a special value which has
implications on data representation; for more information see
[manual.md](manual.md).

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

The following are all the data types currently supported by PyTrackDat.
**Watch out** for additional type-specific settings for some data types.
These often can restrict the possible values that can be stored by the field
in the database, and are useful for data integrity purposes.

Some of these type-specific settings may be **automatically detected** by the
`analyze.py` script; these should be reviewed by hand to make sure they cover
all possible values which can be stored in the field.

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

**No** type-specific settings are available for `integer`.

##### `float`: Floating Point Number (Non-Fixed Precision Decimal)

Floating-point numbers can store a huge range of numbers, including numbers
with decimal points. However, there are precision issues, and
**whenever possible** the `decimal` type should be used instead to prevent
floating-point-specific errors (see [manual.md](manual.md).) 

###### Type-Specific Settings

**No** type-specific settings are available for `float`.

##### `decimal`: Fixed-Precision Decimal Number

Decimal-typed numbers can store fixed-precision decimal numbers. Both the
overall maximum length and decimal precision must be specified, in number of
digits. This type is useful for encoding significant figures and **avoiding**
floating-point-specific errors (see [manual.md](manual.md).)

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

Text fields can store almost any value, unless special restrictions are put in
place to restrict their domain. These fields are often useful in situations
where it does not make sense to restrict the column to certain values; for
example in the case of a `description` field.

Text fields can optionally be limited any combination of:

  1. A certain maximum character length. Values extending beyond this maximum
     length will not be accepted.
     
  1. A list of specific values (think of this as an internal representation of
     a "dropdown"-type input, where only a limited range of values are
     acceptable). For example, consider a specimen table's `sex` field, where
     values should be limited to `male`, `female`, and possibly `unknown`.

These limitations are controlled by the type-specific settings below.

###### Type-Specific Settings

The `text` type optionally can take up two type-specific settings:

  1. `max length`: The maximum length of the contents in the field in terms of
     number of characters.
  1. `options`: A semicolon-separated list of possible values the text field
     can take on. Limiting the domain of a field can be useful in order to
     speed up data entry, prevent typos, and restrict the domain of a field to
     exactly what is desired.

##### `date`: Date

Represents a date, including month and year. Does **not** include any time
information; for times, use a second column with the `time` data type
(described below). At the moment, no timezone information is stored, which
should be tracked manually (or put in the field description.)

Currently, PyTrackDat only accepts the `YYYY-MM-DD` format for dates.

###### Type-Specific Settings

**No** type-specific settings are available for `date`.

##### `time`: Time

Represents a time, including minutes and seconds. If seconds are left out in
any passed values, the default seconds value is `0`. At the moment, no timezone
information is stored, which should be tracked manually (or put in the field
description.)

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

The script will ask if the version being built is a 'production build'. Answer
`n` (no) for now.

It will also prompt for the details of an administrative user. Enter in a
username and password for testing purposes. The 'email' field is optional.

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
source site_env/bin/activate
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

To deactivate the site's virtual environment, type in the following command:

```bash
deactivate
```


### Step 5: Deploying the Application

It is now time to deploy the final version of the application on a server. This
allows the application to be accessed at all times, from anywhere connected to
the internet. User accounts are still used to restrict access to the data. Just
because the server is publically accessible doesn't mean the data is!

There are multiple options for deployment. Below is a guide for deploying on
a new "Virtual Private Server" (VPS) on the DigitalOcean service. For more
advanced users, there is also a guide for deploying on an existing server
(though many of the steps will be similar to DigitalOcean setup).

Instructions are written for Ubuntu Server 18.04 or 16.04 LTS; other
distributions may require slightly different procedures.


#### Deploying the End Result on DigitalOcean

DigitalOcean is a cost-effective VPS (virtual private server) hosting provider.
For $5 USD per month, users can create a server on which the created web
application and database can be hosted. For an additional $1 USD per month,
automatic backups can be enabled.

If you already have a web server on which the application can be deployed, see
the section below.


##### Step 1: Create a DigitalOcean account

Create a DigitalOcean account on their
[signup page](https://cloud.digitalocean.com/registrations/new). Confirm the
email used to create the account.
 
Make sure to enter in payment details that will allow a recurring charge of $5
USD per month (as of the time of writing, the cheapest Droplet/VPS that one can
create) for hosting the application. 


##### Step 2: Create a new droplet (virtual machine)

Once logged into the DigitalOcean dashboard, create a new virtual machine by
clicking the "Create" button and selecting "Droplets".

<img src="images/create_droplet.png" alt="Creating a Droplet" width="400">

Select "Ubuntu 18.04 x64" for the operating system.

<img src="images/select_os.png" alt="Droplet OS Selection" width="500">

For PyTrackDat, the smallest droplet size ($5 USD per month) is more than
adequate, and the most cost effective solution:

<img src="images/droplet_size.png" alt="Droplet Size" width="500">

For an additional $1 USD per month, automatic backups can be enabled to keep
historical versions of the whole droplet. This may be useful for data integrity
and restoring purposes.

<img src="images/backups.png" alt="Droplet Backups" width="500">

Choose a data centre region closest to where most users will be accessing the
database from for maximum performance.

<img src="images/datacentre.png" alt="Data Centre Location" width="500">

Finally, choose a hostname, which can only contain alphanumeric characters,
dashes, and periods. This uniquely identifies the droplet within the account,
and press "Create".

<img src="images/choose_hostname.png" alt="Choose Droplet Hostname" width="500">

An email will be sent to the address used to register the account. It will
contain the newly-created droplet's IP address (4 numbers, separated by
periods) and root password. These are used for **logging in** to the droplet,
and for creating the **production** (final) version of the PyTrackDat
application, which will be uploaded to the server.

TODO: IP ADDRESS, LOGGING IN, SCREENSHOT


##### Step 3: Log into the new droplet and set it up

https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-18-04

TODO


##### Step 3: Install Docker and Docker Compose

TODO

Follow DigitalOcean's [instruction guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04),
following only **steps 1 and 2**. 

TODO

Then, install Docker Compose by following DigitalOcean's [Docker Compose instruction guide](https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04),
following only **step 1**.

TODO


##### Step 4: Build the application's production version (on your own computer)

To build the production version of the database application, the `generate.py`
script must be run again on your **local** computer (i.e. not the new droplet),
this time answering `y` (yes) to the question `Is this a production build?`:

```bash
python3 ./generate.py design.csv site_name
```

The script will prompt for a URL. This must match the URL that will be used to
access the site. It can also be an IP address. Whatever value is specified
should not contain `http://`, `https://`, or a trailing slash.

```
Please enter the production site URL, without 'www.' or 'http://': 
```

TODO: DO-SPECIFIC IP ADDRESS INSTRUCTIONS


##### Step 5: Upload the application

TODO

TODO: MAC OS / LINUX: SCP
TODO: WINDOWS: ????


##### Step 6: Start the application

TODO



#### Deploying the End Result on an Existing Server

TODO


##### Step 1: Install Docker and Docker Compose (If Not Already Done)

TODO

Follow DigitalOcean's [instruction guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04),
following only **steps 1 and 2**. 

TODO

Then, install Docker Compose by following DigitalOcean's [Docker Compose instruction guide](https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04),
following only **step 1**.

TODO


##### Step 2: Build the Application's Production Version

To build the production version of the database application, the `generate.py`
script must be run again on your **local** computer (i.e. not the VM or
server), this time answering `y` (yes) to the question
`Is this a production build?`:

```bash
python3 ./generate.py design.csv site_name
```

The script will prompt for a URL. This must match the URL that will be used to
access the site. It can also be an IP address. Whatever value is specified
should not contain `http://`, `https://`, or a trailing slash.

```
Please enter the production site URL, without 'www.' or 'http://': 
```

If deploying without a domain name, use the IP address when prompted for a URL.


##### Step 2: Upload the Application

TODO


##### Step 3: Start the Application

TODO

TODO: NOTE ABOUT PORTS AND CONFIGURATION



## Updating the Schema

TODO
