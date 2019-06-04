==============================
*(Windows Only)* SSH Utilities
==============================

If you already have SSH and SCP utilities installed, or are not running
Windows, this step can be skipped.

Windows does not include any programs for accessing remote servers or copying
files to them. Both of these actions are needed when deploying a PyTrackDat
application to a remote server. However, there are free utilities available
for download which can help with these tasks.

To download the two utilities needed, visit `KiTTY's download page`_ and
download ``kitty_portable.exe``. Then, visit `WinSCP's download page`_ and
download the portable WinSCP version. Make sure to extract the WinSCP `.zip`
file before running the executable `WinSCP.exe` inside. The first executable
provides a way to access remote servers, and the second executable allows the
copying of files to remote servers.

.. _`KiTTY's download page`: http://www.9bis.net/kitty/?page=Download
.. _`WinSCP's download page`: https://winscp.net/eng/downloads.php


Mini-Tutorial: Using KiTTY
==========================

KiTTY is a tool for logging into and remotely administering servers via a
command-line interface. This remote administration is useful when deploying a
PyTrackDat application to a remote server.

We have prepared [a mini-tutorial](mini-tutorials/KiTTY.md) TODO: RE-LINK
on using KiTTY on a Windows computer.


Mini-Tutorial: Using WinSCP
===========================

WinSCP is a tool for copying files to a remote server using a Windows computer.
A tool similar to this must be used to copy the PyTrackDat application onto a
server for "production" (i.e. real) use.

We have prepared [a mini-tutorial](mini-tutorials/WinSCP.md) TODO: RE-LINK
on using WinSCP.
