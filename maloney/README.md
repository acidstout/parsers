Philip Maloney Parser
=======================
Simple script to download episodes of "Die haarsträubenden Fälle des Philip Maloney" from SRF.


Usage
=======================
You may want to modify the output folder in the script prior running it. After that just run it and it should start downloading.


Requirements
=======================
This Bash script requires the following dependencies to be installed:
- awk
- curl
- grep
- sed
- wget
- xmllint

You can easily install those using

	sudo apt install gawk curl grep sed wget libxml2-utils

Normally the script should run out of the box without the need to install anything as long as you run it from a native Linux system.

If you wish to run it from Windows' UNIX sub-system instead you will at least need to install the libxml2-utils, because they don't come preinstalled.


Known issues
=======================
None so far. If you find one, create an issue for it.


Acknowledgement
=======================
Based on the work of some unknown stranger.
