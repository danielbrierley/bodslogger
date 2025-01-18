# bodslogger

A simple script which logs vehicle tracking data from BODS to a sqlite3 database.

## Database
To create the database, simply run createtables.sql in a new sqlite database

## Config
The script requires the following constants to be assigned:\
config.py - `OPERATORS = `*list of operator shortcodes to log*\
config.py - `LOG_PATH = `*Path to log database*\
key.py - `BODSKEY = `*BODS API Key*
