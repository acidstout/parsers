Dilbert Parser
=======================
Simple script to download the Dilbert comic strips in a defined period of time. If no arguments are passed to the script, it will download all the Dilbert comicstrips until today in the current folder. That will take some time to finish, becuase there are more than 10,000 comics available totalling to more than 1GB of data as of February 2017.


Command line parameters
=======================
-s, --start	Date of first comic to download. Defaults to 1989-04-17.

-e, --end	Date of last comic to download. Defaults to today.

-o, --output	Folder where to put the downloaded comic. Defaults to current folder.


Known issues
=======================
None so far. If you find one, create an issue for it.


Requirements
=======================
This script requires at least Python 3 to run. Also make sure to have the following modules installed:
- dateutil
- imghdr
- urllib
besides the system's default modules.


Acknowledgement
=======================
Based on the work of Alvaro (apadi) @ https://gist.github.com/apadi/d5a12a301b318397a7ed
