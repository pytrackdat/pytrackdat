==========================
Step 3: Database Generator
==========================

Running the Generator
---------------------

The core of PyTrackDat is a database generator script, which uses a provided
CSV design file (see above for the format) to generate a database along with a
web application which can be used to administer it. The generated software is
powered by the `Django framework`_.

To run the database generator on a design file (ex. ``design.csv``), run the
following command:

.. code-block:: bash

   ptd-generate design.csv site_name

Where ``design.csv`` is a path to the design file and ``site_name`` is the name of
the web application that will be generated.

The script will ask if the version being built is a '`production build`_'. Answer
``n`` (no) for now.

It will also prompt for the details of an administrative user. Enter in a
username and password for testing purposes. The 'email' field is optional.

This will output a zip file, ``site_name.zip``, in the PyTrackDat project
directory. This package will be used to deploy the site.

.. _`production build`:

What is a production build?
---------------------------

A "production build" of an application (as opposed to a "development build")
is the version of the application that will be used by all the users of the
program, and is considered a *usable* version. The easiest way to understand
a production build is to consider the opposite, a development build. These
versions of the application are only used for making sure it works.

In the context of PyTrackDat, a production build is one that can be used by
any designated users and will store the "real" data. New data entered will be
considered part of the actual datset. A development build **will not** work
in production, and is simply used to make sure everything works first.

Additional information must be provided to a production PyTrackDat build,
specifically the URL of the server onto which the application will be
deployed (i.e. set up and ran).
**Note about PyTrackDat development builds**
PyTrackDat application development builds cannot export baRcodeR labels from
the web interface. This is a known issue and currently unfixable due to R
and Python compatibility issues.


.. _`Django framework`: https://www.djangoproject.com/
