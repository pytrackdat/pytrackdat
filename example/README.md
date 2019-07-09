# Example PyTrackDat Database, Start to Finish

## Preamble

Make sure you have PyTrackDat installed before trying this example. For
instructions, see the
[installation guide](https://github.com/pytrackdat/pytrackdat#installation).

**Note:** The dataset used here does not contain not real data.


## Generating the Initial Design File

The example dataset here includes two files,
[`specimens.csv`](data/specimens.csv) and [`sites.csv`](data/sites.csv).

The first contains a list of specimens collected from different sites, along
with information about the specimens' species, sex, and collectors, as well as
a collection date.

The second contains a list of sites corresponding with the sites specimens were
sampled from, as well as a set of coordinates for each site. The first file's
`Site Name` column refers to sites listed in the second file.

The first step in the PyTrackDat pipeline is to analyze these files to build
a starting design file, which will be improved upon and used to produce the
final database.

The following command can be ran to produce this "first draft" design file,
[`design_first.csv`](design/design_first.csv):

```bash
ptd-analyze design/design_first.csv specimen data/specimens.csv site data/sites.csv
```

This will yield the following output:

```
PyTrackDat v0.3.0  Copyright (C) 2018-2019 the PyTrackDat authors.
This program comes with ABSOLUTELY NO WARRANTY; see LICENSE for details.

Detecting types for fields in relation 'specimen'...
    Field 'Specimen Number':
        Type: 'manual key'
        Nullable: False
    Field 'Date Collected':
        Type: 'date'
        Nullable: False
    Field 'Species':
        Type: 'text'
        Nullable: False
        Choices: ['Esox lucius', 'Micropterus dolomieu', 'Micropterus salmoides', 'Salvelinus namaycush', 'Sander vitreus']
    Field 'Site Name':
        Type: 'text'
        Nullable: False
        Choices: ['Big Clear Lake', 'Buck Lake', 'Crow Lake', 'Devil Lake', 'Lake Opinicon', 'Little Lake', 'Loon Lake', 'Mosquito Lake', 'Newboro Lake']
    Field 'Sex':
        Type: 'text'
        Nullable: False
        Choices: ['F', 'M', 'U']
    Field 'Collector(s)':
        Type: 'text'
        Nullable: False

Detecting types for fields in relation 'site'...
    Field 'Site Name':
        Type: 'manual key'
        Nullable: False
    Field 'Latitude':
        Type: 'decimal'
        Nullable: False
    Field 'Longitude':
        Type: 'decimal'
        Nullable: False
    Field 'Comments':
        Type: 'text'
        Nullable: False

    Wrote design file to 'design/design_first.csv'...

Analyzed 2 relations.
```

This is a good start! `ptd-analyze` successfully detected the types and choices
for most fields, including nullability, as well as manual keys. Unfortunately,
some details are not handled automatically and are thus not quite right:

  1. The 'Site Name' field in the `specimen` table should be a foreign key,
     since it refers to rows in the `site` table. Therefore, the type for this
     field needs to change and the choices must be deleted (since this is
     handled automatically, by definition of a foreign key.)
     
  2. In the [`design_first.csv`](design/design_first.csv) file itself,
     descriptions are visible for each field. After analysis, each of these is
     set to `!fill me in!`. Good metadata and data handling practices dictate
     that a detailed description should be added for each field, to better
     inform database users and ideally eliminate the chances of inconsistencies
     being introduced into the database in the future.
     

## Improving the Design File

To correct for the issues mentioned above, we can make the following fixes in
the design file. These are visible in the
[`design_final.csv`](design/design_final.csv) file.

  1. Change the type of the 'Site Name' field to `foreign key`, and delete the
     old additional settings. In their place, as per the
     [foreign key data type](https://github.com/pytrackdat/pytrackdat#foreign-key-foreign-key-cross-relation)
     description, we add a single additional setting with the target table (in
     this case `site`) as the value.
     
  2. Add descriptions for each field.

Now that the design file is finalized, we can generate the PyTrackDat site from
the design file and test it, with help from our pre-existing data.


## Generating the Test Database

PyTrackDat generates database web applications from the design file. To
generate a site from the final design file, [`design_final.csv`](design/design_final.csv),
we can run the following command:

```bash
ptd-generate design/design_final.csv test_db
```

This will produce a [Django framework](https://djangoproject.com)-powered
web application archived as `test_db.zip` in the working directory, and
directly accessible in the temporary PyTrackDat work directory,
`tmp/test_db`.


## Running the Test Site

To run the site locally, we can use the following commands, which vary based
on operating system. Following this, you should be able to navigate to
[127.0.0.1:8000](http://127.0.0.1:8000) in your browser to see the test site.

### Linux/macOS

```bash
cd tmp/test_db
source site_env/bin/activate
python ./manage.py runserver
```

### Windows

```cmd
cd tmp\test_db
\site_env\Scripts\activate.bat
python manage.py runserver
```


## Using and Testing the Database

### Importing Data

While generating the database, an account with administrative privileges was
created using the credentials we provided. This account can be used to log into
the site.

The first order of business is to import existing data. Since the `specimen`
table points to the `site` table through a foreign key, it is important that
we import [`sites.csv`](data/sites.csv) **first**, followed by
[`specimens.csv`](data/specimens.csv).

To import data into a table, we first click on the dashboard entry for the
table to access the table-specific management page. An "Import CSV" button
will be present in the upper left corner.

<img src="../images/ptd_import_btn.png" alt="PyTrackDat Import" width="600">

Clicking on this button will bring us to the upload page, where a
CSV-formatted file can be uploaded. Rows in the CSV file will be added to the
database, assuming the CSV file is **formatted correctly**.

### Testing the Site

We should explore the database, clicking on the single-entry add buttons for
each table and making sure it behaves as expected. If any issues arise, edit
the design file to correct them and re-generate the database.


## Deploying the Final "Production" Site

Once the design file and the resulting site are finalized, a "production"
version of the database should be generated. In this case, "production" means
"ready to use with actual data".

For instructions on how to deploy, see the guides on
[deploying on DigitalOcean](https://github.com/pytrackdat/pytrackdat#deploying-the-end-result-on-digitalocean) or
[deploying on an existing or other server](https://github.com/pytrackdat/pytrackdat#deploying-the-end-result-on-an-existing-linux-server).
