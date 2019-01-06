# WinSCP Mini Tutorial for PyTrackDat Setup

TODO: DOWNLOAD

Once WinSCP has been downloaded, double click it to open it. It will show a
window for logging into a server.

For the host name, enter the IP address of the droplet (or the server) being
accessed. For the username and password, use the username and password used to
remotely log into the droplet or server. Then, click Login.

<img src="../images/winscp1.png" width="400">

You may get a popup menu warning you about signing into an unknown server. This
occurs at the first login. It is safe to proceed by pressing "Yes".

<img src="../images/winscp2.png" width="300">

The main window will now be in focus. WinSCP will show a listing of files on
the remote server as well. If the droplet or server is newly created, there
may not be any files visible yet.

In the left-hand pane, locate the ZIP file containing your site using the
location dropdown and popup menus (in the screenshot, `G: KINGSTON` is the
location and `site_name.zip` is the ZIP file in question) and press the Upload
button.

<img src="../images/winscp3.png" width="600">

After the "Upload" button is pressed, a small window will appear with upload
settings. The defaults are fine; press "OK" to continue.

<img src="../images/winscp4.png" width="400">

After pressing "OK", a progress bar will appear showing the file transfer. When
this is done, the file is uploaded!

<img src="../images/winscp5.png" width="400">

Now that the file is uploaded, it should be visible on the remote server, i.e.
the right-hand pane:

<img src="../images/winscp6.png" width="600">

If you see the file on the right, the ZIP file is now on the server! You can
exit out of WinSCP and proceed with unzipping and setting up the PyTrackDat
application.
