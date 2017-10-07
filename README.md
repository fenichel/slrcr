# slrcr

Thrown-together code to figure out where teams are on WSC, using the tracker info from WSC and an elevation profile from Sasha Zbrozek.

Run with python 2.7.

Slrcr_mapping is the most up-to-date version, and outputs a url for a google maps static image.

You'll need to specify the location of the elevation profile CSV and the output file location in slrcr_mapping.py (lines 24 and 26).

You can change the badges that will appear in the static image by editing makeUrl().

You can change the color and labels on the badges by adding cases in makeTeamUrlByName().

Happy hacking!