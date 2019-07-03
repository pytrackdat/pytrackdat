==================================
*(Optional)* Step 1: Data Analyzer
==================================

PyTrackDat includes an automatic data analyzer which can read a one or a series
of CSV files in (i.e. data files with variable names in the headers), as well
as their desired relation names, and generate a PyTrackDat **design file**,
which contains human-readable CSV-formatted instructions for the structure of
the database. This design file is not final, and should be checked over and
added to/edited by a human. However, it provides a good starting point for
generating a database for a particular dataset.

To run the data analyzer on one or more CSV-formatted data files, run the
following command:

.. code-block:: bash

   ptd-analyze design.csv sample_type_1 samples1.csv sample_type_2 samples2.csv [...]


Where ``design.csv`` is the name of the design file to output, and
``sample_type_1`` and ``sample_type_2`` are singular terms for the types of
entries stored in ``samples1.csv`` and ``samples2.csv``, respectively. Feel
free to add more sample types (with corresponding data files) as necessary for
your dataset, or leave out ``sample_type_2`` and ``samples2.csv`` if only one
data type is necessary for the database.
