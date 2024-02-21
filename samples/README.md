# AUVSI-SUAS 2024 GCS 

## Dummy's guide to making drone fly

The missions directory has json files of missions tested so far on simulation as well as on Cleo. Any mission to be flown will be loaded from a json file in this directory.

coverage.py in the coverage director can be run to generate a set of waypoints to perform coverage of a given polygon specified by its boundary coordinates.

scripts contains the python files to be run in Mission PLanner to upload a mission onto the drone and carry out the mission. test.py performs both these tasks, provided the correct paths to the json mission files are provided.

## flyyyyyy 

Assuming appropriate paths and boundary coordinates have been specified
```
python3 coverage/coverage.py 
--In Mission Planner
Under Scripts tab
Select scripts/test.py and run script
```

This will allow you to complete a mission that involves navigating through a set of waypoints and performing coverage of a given polygonal area
