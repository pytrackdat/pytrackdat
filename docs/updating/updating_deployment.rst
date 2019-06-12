============================================
Updating the site on DigitalOcean or similar
============================================

First, export the data currently stored in the web application (if any) via the
online interface. Log into the PyTrackDat application, select all data for each
data type, and export individual CSV files.

The site can then be updated in a similar way to how it was initially uploaded.

First, SSH into the server (see previous instructions on how to do this). How
this is done depends on your operating system.

While logged into the server, change directory into the site:

.. code-block:: bash

   cd site_name


Then, stop the application using Docker Compose:

.. code-block:: bash

   docker-compose down


Go to the parent directory and move the site folder to a backup:

.. code-block:: bash

   cd ..
   mv site_name site_name_old_backup


At this point, you should create (or have created) the new version of the
database. Either change the downloaded CSV files to have the same headers as
the original data files, or re-build the design file using the headers from the
downloaded CSV files. Make sure to re-generate the site using ``ptd-generate``.

Upload the new PyTrackDat application ``.zip`` archive, using methods described
previously in this tutorial.

Follow instructions from the "Deploying..." section above for unzipping the
archive and bringing the application online using Docker Compose.

Finally, re-import the data using the built-in import function in any
PyTrackDat application using the web interface.
