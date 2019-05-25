# Example PyTrackDat Site, Start to Finish

**Note:** The dataset used here does not contain not real data.

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

    Wrote design file to 'design/design_first.csv'...

Analyzed 2 relations.
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

TODO

...

EDIT

...

TODO

```bash
ptd-generate design/design_final.csv test_site
```

TODO: IMPORT DATA (ORDER MATTERS)

TODO: TEST (LINK TO INSTRUCTIONS)

TODO: DEPLOY
