About
=====
This little thingy downloads the c't Uplink HD-video RSS feed and generates a list of wget commands, which download each video and store it using the title of the episode as filename, rather the original cryptic filename. It also creates a log file if requested for each downloaded file. I didn't put much effort into this, so don't expect anything fancy. I just wanted to have a script generate me a list of wget commands, in order not to have to bother around with cryptic filenames anymore.

Known issues
------------
To my mind, PHP is not suitable for this kind of task or at least it's a bad choice for this. You'd better be off using something like Python or Perl. Anyway, I used PHP to show how to read and work with external XML content.

Also I added a Python script which parses the RSS feed and creates a Bash/Batch file to download the videos using wget. It creates the exact same list like the PHP script without the HTML wrapped around.
