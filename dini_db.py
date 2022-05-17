# FILE NAME:    PA5.PY
# AUTHOR:       HOLDEN BOWMAN
# DATE:         MAY 10, 2022
#
# MODIFICATION HISTORY
#
#       MAY 6, 2022
#       - Added methods for parsing
#       - Added methods for argument handling
#       - Created utility methods for arguments
#       - Created methods for file management
#       - Created methods for database management
#       - Created methods for table management
#
#       MAY 7, 2022
#       - Split file into regions
#       - Created methods for input and output
#       - Added additional argument handling methods
#         for alter and select
#       - Added utilities for creating paths
#       - Added exception handling
#       - Added comments to regions, methods, and in-line comments
#
#       MAY 8, 2022
#       - Created PA2 from PA1
#       - Split the files into modules
#       - Enabled parser to read multi-line arguments from file
#       - Created the table management file
#       - Created the table class
#
#       MAY 9, 2022
#       - Added methods for manipulating the table class
#       - Added methods for managing data within tables
#       - Modified selection to properly handle arguments
#       - Created methods for printing table class instances
#       - Created methods for formatting and filtering tables and records
#
#       MAY 9, 2022
#       - Created PA3 from PA2
#       - Added a Record class
#       - Implemented methods for assisting in joins
#       - Added inner joins
#       - Added right and left outer joins
#       - Changed logic for the select function

#       MAY 9, 2022
#       - Created PA4 from PA3
#       - Added methods for beginning, aborting, and committing
#       - Added transaction globals to _tablemanagement.py
#       - Added key generation to transactions
#       - Modified transaction checking
#       - Changed how tables are read and updated
#
#       MAY 10, 2022
#       - Created PA5 from PA4
#       - Added methods for finding the count, max, min and average of a table
#       - Adjusted the way arguments are split
#       - Implemented COUNT, AVG, MAX and MIN in select_record()


import argparse
import logging
import _globals as _gl
import _filesystem as _fs
import _dbmanagement as _db
import _input as _in

# region ARGPARSER ARGUMENTS

# REGION:       ARGPARSER ARGUMENTS
# DESCRIPTION:  Contains the argparser and its arguments

parser = argparse.ArgumentParser()

parser.add_argument(
    '-f', '--file',
    type=str,
    default=None
)

parser.add_argument(
    '-r', '--reset',
    help="Resets the database upon initialization",
    action="store_const", dest="reset", const=True,
    default=False,
)

parser.add_argument(
    '-d', '--debug',
    help="Set log level to logging.DEBUG",
    action="store_const", dest="loglevel", const=logging.DEBUG,
    default=logging.WARNING,
)

parser.add_argument(
    '-v', '--verbose',
    help="Set log level to logging.INFO",
    action="store_const", dest="loglevel", const=logging.INFO,
)

ARGS = parser.parse_args()

logging.basicConfig(level=ARGS.loglevel)

# endregion

# region PROGRAM

# REGION:       PROGRAM
# DESCRIPTION:  Initializes, runs, and ends the program

# --------- METHODS --------- #


# METHOD:       main()
# DESCRIPTION:  Program entry point
# ARGUMENTS:    N/A
# RETURNS:      N/A
def main():
    # Initialize the program
    init()

    # Enter program execution loop
    run()

    # Performs any steps necessary at end of program's execution
    end()


# METHOD:       run()
# DESCRIPTION:  Runs the program's loop as a part of main's execution
# ARGUMENTS:    N/A
# RETURNS:      N/A
def run():
    # If a file is specified from the program's arguments, read from that file
    # In the case that an '.EXIT' command is not read from the file, continue from terminal
    if ARGS.file is not None:
        if not _in.file_input(ARGS.file):
            return

    # Takes in user input from the terminal
    _in.terminal_input()


# METHOD:       init()
# DESCRIPTION:  Initializes the program as a part of main's execution
# ARGUMENTS:    N/A
# RETURNS:      N/A
def init():
    logging.info('Performing initialization...')

    # Initialize global variables in modules that use globals
    _gl.gl_init()
    _fs.fs_init()
    _db.db_init()

    # If the reset argument in the argparser is set, reset the default database
    # Raises an exception in the case of an invalid directory
    if ARGS.reset:
        _db.reset_databases_folder()

    # Create the default database directory if it doesn't exist
    _db.initialize_databases_folder()


# METHOD:       end()
# DESCRIPTION:  End the program at the end of main's execution
# ARGUMENTS:    N/A
# RETURNS:      N/A
def end():
    print('All done.')


# endregion

# region COMMENT TEMPLATES

# REGION:
# DESCRIPTION:

# --------- METHODS --------- #

# METHOD:
# DESCRIPTION:
# ARGUMENTS:
# RETURNS:

# endregion
if __name__ == '__main__':
    main()
