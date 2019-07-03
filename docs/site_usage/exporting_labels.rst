==============================
Exporting Labels with baRcodeR
==============================

`baRcodeR`_ is an R package for labeling, tracking, and organizing samples
based on 2D barcodes (QR codes). In production, a PyTrackDat application
allows users to export labels for database table entries based on values of the
table's **primary key**. This allows for the unique identification of physical
objects (e.g. samples), linking them to their corresponding database entries.

To export baRcodeR labels from a PyTrackDat application, first click on the
dashboard entry for the table you wish to export labels for. Select all data
that you wish to label using the checkboxes available.

.. figure:: ../_static/ptd_export.png
   :width: 600
   :alt: PyTrackDat Export

Then, use the dropdown action menu to select the "Export baRcodeR labels (PDF)
for selected" action and click "Go". This will download a PDF file onto your
local computer with the QR code labels.

.. figure:: ../_static/ptd_barcodes.png
   :width: 600
   :alt: PyTrackDat Barcodes


.. _`baRcodeR`: https://github.com/yihanwu/baRcodeR
