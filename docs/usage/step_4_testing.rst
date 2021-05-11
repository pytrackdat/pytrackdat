===============
Step 4: Testing
===============


Starting the Test Server
------------------------

To test a design file called ``my_design.csv``, run the following command:

.. code-block:: bash

   pytrackdat test my_design.csv

A development server will run on your local machine at port 8000, meaning it
can be accessed in a web browser at ``http://localhost:8000/``.


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
