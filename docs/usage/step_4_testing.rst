===============
Step 4: Testing
===============

The Quick Way
-------------

PyTrackDat provides a script which helps test newly-created sites from the root
PyTrackDat working directory. To test a site named ``site_name_here``, run the
following command:

.. code-block:: bash

   ptd-test site_name_here


The Manual Way
--------------

If for some reason the method above fails, the following manual procedure can
be employed to test a PyTrackDat site.

To test the web application from the PyTrackDat directory, first change to the
site directory within the temporary work directory, ``tmp``, which PyTrackDat
will create, replacing ``site_name_here`` with the site name that you assigned in
the previous (generator) step. Then, activate the Python virtual environment.
These actions can be done with the following commands:



**macOS/Linux:**

.. code-block:: bash

   cd tmp/site_name_here
   source site_env/bin/activate


**Windows:**

.. code-block:: bat

   cd tmp\site_name_here
   site_env\Scripts\activate.bat


Then, run the development server from the command line with the following
command, and navigate to the application in your web browser at
``127.0.0.1:8000``:

**macOS/Linux:**

.. code-block:: bash

   python3 ./manage.py runserver


**Windows:**

.. code-block:: bat

   python manage.py runserver


Afterwards, when testing is finished, to deactivate the site's virtual
environment, run the following command:

.. code-block:: bash

   deactivate



When the Server is Running
--------------------------

While the development server is running, you can explore the site the same way
you will be able to once it is finalized and deployed on a server. This is the
time to check and make sure the data format is correct, importing and exporting
your data works, and everything is behaving as expected.

Here is an overview checklist of what should be verified using this development
version of the application

1. The data format, including names, descriptions, and types appears correct
   and corresponds with what will appear in the data file imported.

2. All necessary tables are present.

3. All foreign keys (inter/intra-table links) are correct and work as
   expected.

4. Data types with an enforced choice of values include all desired choices,
   including ones for future data that **may not be used yet**.

5. Data import works with data CSV files (if applicable).

6. Data export works and appears as expected.

Once you are done verifying, the server can be stopped. To do this, press
``Ctrl-C`` in the terminal window where the server is running.
