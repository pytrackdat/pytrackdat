===================
Updating the Schema
===================

PyTrackDat applications have the ability to export CSV files from tables. These
files are in a standard header-list of entries CSV format, so to update the
schema (i.e. add or remove columns), the following procedure can be used:

1. Export all tables as CSV files using the PyTrackDat-supplied action in the
   web interface.

2. Either use the downloaded CSV files in the ``ptd-analyze`` script to
   generate a new design file or use your original design file. Make sure to
   restore any foreign keys (and other changes) from before if starting anew.

3. Modify the design file to include any desired modifications, such as new
   or altered columns. If needed, modify the CSV files to reflect renamed
   or deleted columns. Make sure to make columns nullable/blank-able if
   you are not providing values for all existing entries in the database.

4. Follow the instructions from elsewhere in this document to generate a new
   site. Replace the application using the instructions below.

5. Import data using the "Import CSV" action provided by PyTrackDat. This
   should restore data to the original state from before the changes,
   except with any changes in the design file reflected in the new
   application.
