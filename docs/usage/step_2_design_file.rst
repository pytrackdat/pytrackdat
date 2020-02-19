============================================
Step 2: Design File Layout and Customization
============================================

A PyTrackDat design file contains specifications for all tables in the database
within a single CSV file. The file consists of **blocks**, each of which
corresponds to the specification for a single table, based on each of the CSV
files passed to the script. Blocks are separated by blank lines.

A single block may look like this:

+-----------+----------------+-------------+-----------+-------------+---------+----------------------------------+----------------+----------------------+
| my_sample | new field name | data type   | nullable? | null values | default | description                      | show in table? | additional fields... |
+===========+================+=============+===========+=============+=========+==================================+================+======================+
| Date      | date           | integer     | false     |             |         | Date the sample was collected.   | true           |                      |
+-----------+----------------+-------------+-----------+-------------+---------+----------------------------------+----------------+----------------------+
| Site ID   | site_id        | foreign key | false     |             |         | Site where the sample was found. | true           |                      |
+-----------+----------------+-------------+-----------+-------------+---------+----------------------------------+----------------+----------------------+
| ...                                                                                                                                                     |
+-----------+----------------+-------------+-----------+-------------+---------+----------------------------------+----------------+----------------------+

Design files should **not** be left as-is after generation via ``ptd-analyze``.
The script does its best to infer data types from the columns, but is not
guaranteed to do this perfectly. Additionally, it is best practice to add a
**field description** (under the *description* header) to provide human users
additional information about what type of data is stored in the field.

For each generated design file, users should examine the file using the
following checklist:

1. Check that data types and type-specific options are correct for each field
2. Add human-readable **descriptions** for each field
3. Change desired **foreign keys** from their detected data type to the foreign
   key data type, following the `foreign key documentation <foreign-key-ref_>`_
   to link them to the correct table.


Design File Customization
=========================

In almost all cases, there are data types and settings that will be impossible
for the ``analyze.py`` script to detect. For example, a **foreign key**, which
is a data type that allows a row in a table to refer to a different row in
either the same table or a different table, cannot be automatically detected.
Foreign keys are very useful for reducing data duplication and encoding complex
data relationships.

In other cases, it may be desirable to limit a field to a range of data types.
For example, if a specimen can be one of four species, it is desirable to make
a text field which can only store any of these four species' names. The analyze
script does its best to detect these instances, but it may not detect
**all possible choices**. Thus, text fields with automatically-detected choice
limitations should be verified manually and if needed, edited.


Design File Specification
=========================


Blocks
------

Blocks must be separated by at least one blank line in the CSV (i.e. 2
newlines.)


Block: First Row
^^^^^^^^^^^^^^^^

The first row of a block contains only one piece of information: the name of
the entity being represented, in singular form (for example, "sample")
contained in the first column. The other columns of the block's first row are
ignored, but can be used as column headers to make the design file more
human-readable.

Thus, a block's first (header) row may look like this:

+------------+-----------------+------------+-----+
| **sample** | this is ignored | as is this | ... |
+------------+-----------------+------------+-----+


Block: Following Rows – Field Descriptions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following series of rows in a design file block contain a list of field
descriptions, which are analogous to columns in a standard spreadsheet layout.
Each database field corresponds to each one of these rows in the design file.

The generic format for a design file field description row is the following:

+-----------------+---------------------+-----------+-----------+-------------+---------+-------------+----------------+----------------------+
| CSV Column Name | Database Field Name | Data Type | Nullable? | Null Values | Default | Description | Show in Table? | Additional fields... |
+-----------------+---------------------+-----------+-----------+-------------+---------+-------------+----------------+----------------------+

Each of these columns in the field description row has specific acceptable
values which directly decide the resulting database structure. As such, it is
important to double-check these values if the automatic analyzer is used.

CSV Column Name
"""""""""""""""

This cell should correspond exactly to the column name in the original data
CSV file which stores data for field being described.

Database Field Name
"""""""""""""""""""

This cell contains the name of the field as it will appear in the database (as
decided by the ``analyze.py`` script). It should only contain lowercase
characters, numbers, and underscores.

Data Type
"""""""""

This cell contains the data type of the field in question. It can assume one of
the following values:

- ``auto key``
- ``manual key``
- ``foreign key``
- ``integer``
- ``float``
- ``decimal``
- ``boolean``
- ``text``
- ``date``
- ``time``

Nullable?
"""""""""

This cell contains a boolean (true or false) value which specifies whether the
value of the field in the database can be ``NULL``. If the field contains any
value other than "true", "false" is inferred. Null is a special value which has
implications on data representation.

A variable field is **nullable** if it can be assigned either a value or
``null``, signifying that for a specific table row (e.g. an individual or
observation) there is no value assignable.

Null Values
"""""""""""

This cell contains a semicolon-separated list (``;``, optionally with
surrounding spaces to make the cell contents more readable) of values in the
data CSV file which will be converted to a ``NULL`` value in the database.

Note that if this cell contains multiple entries, **information is being lost**,
since multiple values in the original data are mapped to a single value in the
database, thus preventing the original data from being recovered identically.

An example of where multiple values could be useful is the following::

    NA; N/A

In this case, these two values mean the same thing to a human reader but are
completely different to the computer. If ``NA`` is, for example, the only
possible non-integer value in an integer field, it would make sense to map it
to ``NULL``.

Default
"""""""

This cell contains a value, of the same type as would appear in the data CSV
file, specifying the default value for the field in the database.

Default values are used as the starting point when inputting a value into a
field in the GUI.

.. figure:: ../_static/default.png
   :width: 400
   :alt: Example of a default value

These values are also used when no value is provided for a field when importing
a CSV file. Don't set a default if you want a blank CSV entry to stay blank (or
``null``, depending on settings) in the database.

Description
"""""""""""

This cell should contain a succinct and comprehensive description of what the
field means in the context of the dataset the database is to contain, including
explanations of possible values if non-obvious.

It is also used to display help text below the fields in the database
single-item entry GUI.

Show in Table?
""""""""""""""

This cell contains a boolean (true or false) value which specifies whether the
field in question should appear in the table list view (where a list of all
rows is shown.) If left blank, the cell will **not** appear.

Type-Specific Settings
""""""""""""""""""""""

Any cell after the description cell is type-specific and the valid values
depend on what data type the field has. There can be more than one
type-specific setting available, and the exact number also depends on the
field's type. For a description of each data type, including type-specific
setting options, see below.


Data Type Descriptions
----------------------

The following are all the data types currently supported by PyTrackDat.
**Watch out** for additional type-specific settings for some data types.
These often can restrict the possible values that can be stored by the field
in the database, and are useful for data integrity purposes.

Some of these type-specific settings may be **automatically detected** by the
``ptd-analyze`` script; these should be reviewed manually to make sure they
cover all possible values which can be stored in the field.

``auto key``: Automatic Primary Key
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Automatic primary key (identifier) for a database row; stored as an integer
which starts at 1 and is increased by 1 for every row added to a table.

Deletion of a row does not lead to re-assigning IDs above the now-deleted row's
ID; IDs are fixed as long as the database is not completely re-created.

Design File Information
"""""""""""""""""""""""

The following design file cells are **ignored** for ``auto key``:

- CSV Column Name
- Nullable
- Null Values
- Default

Automatic primary keys are **never** nullable.

Type-Specific Settings
""""""""""""""""""""""

**No** type-specific settings are available for ``auto key``.

``manual key``: Manually-Specified Primary Key
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Manually-specified primary key (identifier, e.g. a unique collection number, a
sample numer in a tissue archive, or some other uniquely-identifying piece of
information for each row in the table) for a database row; stored as text. The
value must be specified by the user when adding data to the database.

Manually-specified primary keys must be **unique** for a given row
(/observation).

Design File Information
"""""""""""""""""""""""

The following design file cells are **ignored** for ``manual key``:

- Nullable
- Null Values
- Default

Manually-specified primary keys are **never** nullable.

Type-Specific Settings
""""""""""""""""""""""

**No** type-specific settings are available for ``manual key``.

``integer``: Integer (Negative or Positive Whole Number)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Integers can be between -9 223 372 036 854 775 808 and
9 223 372 036 854 775 807. If a bigger-capacity field is needed, use a
``text``-type field instead.

Type-Specific Settings
""""""""""""""""""""""

**No** type-specific settings are available for ``integer``.

``float``: Floating Point Number (Non-Fixed Precision Decimal)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Floating-point numbers can store a huge range of numbers, including numbers
with decimal points. However, there are precision issues, and
**whenever possible** the ``decimal`` type should be used instead to prevent
floating-point-specific errors.

Type-Specific Settings
""""""""""""""""""""""

**No** type-specific settings are available for ``float``.

``decimal``: Fixed-Precision Decimal Number
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Decimal-typed numbers can store fixed-precision decimal numbers. Both the
overall maximum length and decimal precision must be specified, in number of
digits. This type is useful for encoding significant figures and **avoiding**
floating-point-specific errors.

Type-Specific Settings
""""""""""""""""""""""

The ``decimal`` type requires two type-specific settings:

1. ``max_length``: The maximum length a number can be, in digits; includes the
   decimal portion of the number.

2. ``precision``: The number of digits after the decimal. Will be the same for
   any value stored in the database, with the end 0-padded if necessary.

For example, a ``decimal`` field with a ``max length`` of 10 and a ``precision`` of 4
can store numbers such as ``50.2300`` or ``-999999.9999`` or ``999999.9999`` (as a
negative sign does not count as a digit) but **cannot** store ``1000000.0000``
because it is too long.

``boolean``: Boolean (True or False) Value
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Boolean values are either ``true`` or ``false``. If the field is made nullable, an
additional option is added, ``NULL`` (or unknown). If more than 3 values are
needed (for example if there are two types of unknown values), a text field
with the ``choices`` setting should be used.

Type-Specific Settings
""""""""""""""""""""""

**No** type-specific settings are available for ``boolean``.

``text``: Fixed- or Unbounded-Length Text
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Text fields can store almost any value, unless special restrictions are put in
place to restrict their domain. These fields are often useful in situations
where it does not make sense to restrict the column to certain values; for
example in the case of a ``description`` field.

Text fields can optionally be limited by any combination of:

1. A certain maximum character length. Values extending beyond this maximum
   length will not be accepted.

2. A list of specific values (think of this as an internal representation of
   a "dropdown"-type input, where only a limited range of values are
   acceptable). For example, consider a specimen table's ``sex`` field, where
   values should be limited to ``male``, ``female``, and possibly ``unknown``.

These limitations are controlled by the type-specific settings below.

Type-Specific Settings
""""""""""""""""""""""

The ``text`` type optionally can take up two type-specific settings:

1. ``max_length``: The maximum length of the contents in the field in terms of
   number of characters.

2. ``options``: A semicolon-separated list of possible values the text field
   can take on. Limiting the domain of a field can be useful to speed up data
   entry, prevent typos, and restrict the domain of a field to exactly what
   is desired.

``date``: Date
^^^^^^^^^^^^^^

Represents a date, including month and year. Does **not** include any time
information; for times, use a second column with the ``time`` data type
(described below). At the moment, no timezone information is stored, which
should be tracked manually (or put in the field description.)

**Currently, PyTrackDat only accepts the ``YYYY-MM-DD`` format for dates.**

Type-Specific Settings
""""""""""""""""""""""

**No** type-specific settings are available for ``date``.

``time``: Time
^^^^^^^^^^^^^^

Represents a time, including minutes and seconds. If seconds are left out in
any passed values, the default seconds value is ``0``. At the moment, no timezone
information is stored, which should be tracked manually (or put in the field
description).

Currently, PyTrackDat **only accepts** the ``HH:MM`` or ``HH:MM:SS`` **24 hour**
formats for times.

Type-Specific Settings
""""""""""""""""""""""

**No** type-specific settings are available for ``time``.

.. _foreign-key-ref:

``foreign key``: Foreign Key (Cross-Relation)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Foreign keys are one of the most powerful features of relational databases, and
in fact are what make then "relational" at all. A foreign key is a field on one
table which refers to the **primary key** of a row in *another* table (and in
fact, can refer to another row in the *same* table as well.)

This lets rows refer to one another, and can be used to prevent data
duplication. Reducing data duplication is important in preventing contradictory
information in a dataset.

Type-Specific Settings
""""""""""""""""""""""

The ``foreign key`` type requires one type-specific setting:

1. ``target``: The table which the foreign key field is pointing to. Remember
   that table names are specified in the first column of the first row of
   a block in the design file.

For example, if a row in a table called ``sample`` refers to a row in a table
called ``site``, the ``target`` setting would be ``site``. This could have the
semantic meaning that, whenever a value is present in a row with the
``foreign key`` field set, that ``sample`` entry was collected at the specified
``site`` entry (representing an actual collection site).

This allows rows to be linked together. ``target`` **does not** have to refer to
a different table; the same table could be specified, allowing rows in a table
to link to other rows in the same table.