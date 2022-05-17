# FILE NAME:    _FILESYSTEM.PY
# MODULE NAME:  File System
# DESCRIPTION:  Provides methods for managing the files of the databases
# AUTHOR:       HOLDEN BOWMAN
# DATE:         MAY 7, 2022

import os
import shutil
import logging
import _globals

# region FILE MANAGEMENT

# REGION:       FILE MANAGEMENT
# DESCRIPTION:  Provides methods for validating, creating and deleting files and folders

# --------- METHODS --------- #


# METHOD:       validate_directory()
# DESCRIPTION:  Checks to see if a directory exists
# ARGUMENTS:    directory - a path to the directory
# RETURNS:      A bool representing whether the directory exists or not
def validate_directory(directory):
    return os.path.isdir(directory)


# METHOD:       create_directory()
# DESCRIPTION:  Creates a directory at the specified path
# ARGUMENTS:    directory - the path to the directory
# RETURNS:      A bool representing the success of the operation
def create_directory(directory):
    # Checks to see if the directory could successfully be created
    # If so, return true
    # Otherwise, return false
    try:
        logging.info(f'Attempting to create directory {directory}')
        os.mkdir(directory)
        logging.info(f'Successfully created directory {directory}')
        return True
    except OSError as error:
        logging.info(f'WARNING:The directory {directory} could not be created due to an OSError')
        return False


# METHOD:       delete_directory(directory)
# DESCRIPTION:  Deletes a directory at the specified path
# ARGUMENTS:    directory - the path to the directory
# RETURNS:      A bool representing the success of the operation
def delete_directory(directory):
    # Checks to see if the directory could successfully be deleted
    # If so, return true
    # Otherwise, return false
    try:
        logging.info(f'Attempting to delete directory {directory}')
        shutil.rmtree(directory)
        logging.info(f'Successfully deleted directory {directory}')
        return True
    except OSError as error:
        logging.info(f'The directory {directory} could not be deleted due to an OSError')
        return False


# METHOD:       validate_files()
# DESCRIPTION:  Checks to see if a file exists
# ARGUMENTS:    directory - a path to the directory
# RETURNS:      A bool representing whether the file exists or not
def validate_file(directory):
    return os.path.isfile(directory)


# METHOD:       create_file()
# DESCRIPTION:  Creates a file at the specified path
# ARGUMENTS:    directory - the path to the file
# RETURNS:      A bool representing the success of the operation
def create_file(file):
    # Checks to see if the file could successfully be created
    # If so, return true
    # Otherwise, return false
    try:
        open(file, 'x')
        return True
    except FileExistsError:
        logging.info(f'WARNING:The file {file} could not be created due to an OSError')
        return False


# METHOD:       delete_file()
# DESCRIPTION:  Deletes a file at the specified path
# ARGUMENTS:    directory - the path to the file
# RETURNS:      A bool representing the success of the operation
def delete_file(file):
    # Checks to see if the file could successfully be deleted
    # If so, return true
    # Otherwise, return false
    try:
        logging.info(f'Attempting to delete file {file}')
        os.remove(file)
        logging.info(f'Successfully deleted file {file}')
        return True
    except FileNotFoundError as error:
        logging.info(f'WARNING:The file {file} could not be deleted due to an OSError')
        return False


# endregion

# region FILE IO

# REGION:       FILE IO
# DESCRIPTION:  Provides methods for file input and output

# --------- METHODS --------- #

# METHOD:       read_file()
# DESCRIPTION:  Reads a file from the specified path
# ARGUMENTS:    path - the path of the file to read
# RETURNS:      N/A
def read_file(path):
    # Reads the file, provided it exists, and returns the list of lines as strings
    # If an exception is raised, abort
    try:
        return open(path, 'r').readlines()
    except FileNotFoundError:
        logging.info('File could not be read because it does not exists')
        return []


# METHOD:       write_line()
# DESCRIPTION:  Writes a line to a specified file
#               Can be used to echo output to the terminal
# ARGUMENTS:    output - the text output
#               file - the specified file path
#               echo - echo output to the console
#               append - use append mode if true, write mode of false
# RETURNS:      N/A
def write_line(output='', file=None, echo=False, append=True):
    # Guard clause that aborts if the output is not a string
    if not isinstance(output, str):
        logging.info('Output for write_line is not a string!')
        return

    # Echo to console of the echo bool is set to true
    if echo:
        print(output)

    # If a file was set, then write to the file
    # Mode for open is dependent on the 'append' parameter
    # Will raise exception if something goes wrong
    if file is not None:
        try:
            f = open(file, 'a' if append else 'w')
            if output != '':
                f.write(f'{output}\n')
        except FileExistsError as fee_error:
            logging.info(f'WARNING:The file {file} could not be created due to a FileExistsError')
            raise fee_error
        except FileNotFoundError as fnf_error:
            logging.info(f'WARNING:The file {file} could not be accessed to due to a FileExistsError')
            raise fnf_error

# endregion

# region UTILITY

# REGION:       UTILITY
# DESCRIPTION:  The utility section provide easy to use methods that reduce
#               the overall amount of code required for repetitive tasks and
#               allow for much cleaner code.

# --------- METHODS --------- #


# METHOD:       _path()
# DESCRIPTION:  Utility method for joining a list of strings into a file path
# ARGUMENTS:    arg1 - the first string of the path to create
#               argv - variable number of string to assemble a path from
# RETURNS:      A string representing the path assembled from the arguments
def _path(arg1, *argv):
    # p - the first part of the path to assemble from the arguments
    p = arg1

    # For each argument provided, append it to the path
    for arg in argv:
        p = os.path.join(p, arg)

    # Return the newly assembled path
    return p.lower()


# METHOD:       rpath()
# DESCRIPTION:  Utility method for joining a list of strings into a file path relative to the current directory
# ARGUMENTS:    argv - variable number of string to assemble a path from
# RETURNS:      A string representing the path assembled from the arguments
def rpath(*argv):
    return _path(os.getcwd(), *argv)


# endregion

# METHOD:       fs_init()
# DESCRIPTION:  Initializes the file system global variables used by the program
# ARGUMENTS:    N/A
# RETURNS:      N/A
def fs_init():
    _globals.CURRENT_DIRECTORY = os.getcwd()
