# Cyanide &amp; Happiness Parser
Parses the Cyanide and Happiness webiste and downloads all comic strips. Allows to specify start and end id of comic strips as well as download folder.

Defaults to first known comic strip id as start id, and uses the id of the latest comic strip as end id. If a download folder has been specified, it will be created unless it already exists.

In order to speed up resuming an aborted download a list of all processed comic ids will be saved in the cnh.dat file, which will be created in the same folder where the script is.
