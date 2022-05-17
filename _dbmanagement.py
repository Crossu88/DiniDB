import logging
import re
import os
import shutil
import _globals
import _utils
import _filesystem

# region DATABASE MANAGEMENT

# REGION:       DATABASE MANAGEMENT
# DESCRIPTION:  Provides methods for managing the databases folder

# --------- METHODS --------- #


# METHOD:       reset_databases_folder()
# DESCRIPTION:  Deletes the current default databases directory if it exists,
#               this allows the program to run off of a clean slate for the
#               purposes of reading from test scripts
# ARGUMENTS:    N/A
# RETURNS:      N/A
def reset_databases_folder():
    logging.info('Resetting databases...')

    # default_database_dir - the path to the default database folder
    default_database_dir = _filesystem.rpath(_globals.DATABASES_DIRECTORY)

    # If the reset argument in the argparser is set, reset the default database
    # Raises an exception in the case of an invalid directory
    try:
        shutil.rmtree(default_database_dir)
        logging.info('Deleting default databases folder')
    except OSError as error:
        logging.info('Could not delete default databases folder')


# METHOD:       initialize_databases_folder()
# DESCRIPTION:  Initializes the default databases directory if it does not already exist
# ARGUMENTS:    N/A
# RETURNS:      N/A
def initialize_databases_folder():
    logging.info("Creating default database directory...")

    # default_database_dir - the path to the default database folder
    default_database_dir = _filesystem.rpath(_globals.DATABASES_DIRECTORY)

    # If the default database directory does not exist, create the default databases folder
    if _filesystem.create_directory(default_database_dir):
        logging.info("Default database directory has been created")
    else:
        logging.info("Default database directory already exists")


# endregion

# region DATABASES

# REGION:       DATABASES
# DESCRIPTION:  Provides methods for setting, validating, creating and deleting databases

# --------- METHODS --------- #


# METHOD:       use_database()
# DESCRIPTION:  Sets the database being used
# ARGUMENTS:    name - the name of the database to use
# RETURNS:      N/A
def use_database(name: str = ''):
    # Guard clause that aborts if the name is an empty string or None
    if name is None or name == '':
        print(f'!Failed because the database "{name}" is invalid')
        _globals.active_db = None
        return

    logging.info(f'Attempting to use database "{name}"...')

    # Confirm that the database exists, then sets the 'active_db' global variable
    # If the database does not exist, set the 'active_db' global variable to None
    if validate_database(name):
        _globals.active_db = name
        print('Using database ' + name + '.')
    else:
        _globals.active_db = None
        print('!Failed to use ' + name + ' because the database does not exist.')


# METHOD:       validate_database()
# DESCRIPTION:  Validates the existence of a database
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      A bool representing whether the database exists or not
def validate_database(arguments):
    # Takes the database name from the list of arguments, discarding any remaining arguments
    database_name, _ = _utils.pop_argument(arguments)

    # directory_name - the path to the database's folder
    directory_name = _filesystem.rpath(_globals.DATABASES_DIRECTORY, database_name)

    logging.info(f'Validating existence of database: {database_name}')

    # Checks the files to see if the database's folder exists
    return _filesystem.validate_directory(directory_name)


# METHOD:       create_database()
# DESCRIPTION:  Creates a database
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      N/A
def create_database(arguments):
    # Takes the database name from the list of arguments, discarding any remaining arguments
    database_name, _ = _utils.pop_argument(arguments)

    # directory_name - the path to the database's folder
    directory_name = _filesystem.rpath(_globals.DATABASES_DIRECTORY, database_name)

    logging.info(f'Attempting to create database: {database_name} at {directory_name}')

    # If the database was created, print the success message to the console
    # Otherwise, print an error message
    if _filesystem.create_directory(directory_name):
        print("Database " + database_name + " created.")
    else:
        print("!Failed to create database " + database_name + " because it already exists.")


# METHOD:       drop_database()
# DESCRIPTION:  Deletes a database
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      N/A
def drop_database(arguments):
    # Takes the database name from the list of arguments, discarding any remaining arguments
    database_name, _ = _utils.pop_argument(arguments)

    # directory_name - the path to the database's folder
    directory_name = _filesystem.rpath(_globals.DATABASES_DIRECTORY, database_name)

    logging.info(f'Attempting to delete database: {database_name}')

    # If the database was deleted, print the success message to the console
    # Otherwise, print an error message
    if _filesystem.delete_directory(directory_name):
        print("Database " + database_name + " deleted.")
    else:
        print('!Failed to delete database ' + database_name + ' because it does not exist.')


# endregion

# region TABLES

# REGION:       TABLES
# DESCRIPTION:  Provides definitions for table operations

# --------- METHODS --------- #

# METHOD:       generate_table_meta()
# DESCRIPTION:  Generates the metadata string for a table using a regular expression
# ARGUMENTS:    parameters - a string representing the parameters
# RETURNS:      The metadata string
def generate_table_meta(parameters):
    # Finds each of the fields for the metadata string using a regular expression
    # The 'args' variable will then contain a list of the fields
    args = re.findall(r'\w+\s\w+(?:\(\w+\))*', parameters)

    # Join the fields into a singular string
    meta = '|'.join(args)

    # Provided the metadata is a string, return it
    # Otherwise, return an empty string
    return meta if isinstance(meta, str) else ''


# METHOD:       alter_table_meta()
# DESCRIPTION:  Modifies the table meta string of a table
# ARGUMENTS:    meta - the table metadata string
#               param - the new parameter
# RETURNS:      A string containing the new metadata
def alter_table_meta(meta, param):
    # Appends a field to the table metadata string provided
    return f'{meta}|{param}'


# METHOD:       validate_table()
# DESCRIPTION:  Validates the existence of a table
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      A bool representing whether the table exists or not
def validate_table(arguments):
    # Takes the table name from the list of arguments, discarding any remaining arguments
    table_name, _ = _utils.pop_argument(arguments)

    # path - the path to the table in the database's folder
    path = tbl_path(table_name)

    # Returns whether the file exists or not
    return _filesystem.validate_file(path)


# METHOD:       alter_table()
# DESCRIPTION:  Alters the table metadata
# ARGUMENTS:    arguments - the list of argument strings
# RETURNS:      N/A
def alter_table(arguments):
    # Guard clause that aborts if no database is being used
    if _globals.active_db is None:
        print("!Failed because no database is being used.")
        return

    # table_name - the name of the table taken from the arguments
    # args_list - the remaining arguments without the first argument
    table_name, args_list = _utils.pop_argument(arguments)

    # operation - the operation being performed to alter the table
    operation, param = _utils.pop_argument(args_list)

    # parameter - the field to add to the table metadata
    parameter = ' '.join([param[0], param[1]])

    # file_path - the file path to the table in the database
    file_path = tbl_path(table_name)

    # Stub logic since the alter_table function will only receive 'ADD' for PA1
    # Reads in the first line of the file which contains the table metadata
    # Then, alter that metadata by adding a field to the metadata string
    # If that field with the same name has already been declared, print an error message
    # Otherwise, print a success message
    try:
        f = open(file_path, 'r')
        old_meta = f.readline().strip()
        f.close()
        if param[0] in old_meta:
            print(f'!Failed because the field {param[0]} has already been declared')
        else:
            new_meta = alter_table_meta(old_meta, parameter)
            print(f'Table {table_name} modified.')
            _filesystem.write_line(new_meta, file_path, echo=False, append=False)
    except FileNotFoundError as err:
        print(f'!Failed to modify {table_name} because it does not exist!')


# METHOD:       create_table
# DESCRIPTION:  Creates a table within the database
# ARGUMENTS:    arguments - the list of argument strings
# RETURNS:      N/A
def create_table(arguments):
    # Guard clause that aborts if no database is being used
    if _globals.active_db is None:
        print("!Failed because no database is being used.")
        return

    # table_name - the name of the table taken from the arguments
    # args_list - the remaining arguments without the first argument
    table_name, args_list = _utils.pop_argument(arguments)

    # file_path - the path to the table file in the database
    file_path = tbl_path(table_name)

    # data - the data string that will become the table's metadata
    data = args_list.strip('() \n')

    # meta - the metadata string that will be placed in the table
    meta = generate_table_meta(data)

    # If the meta is not None and the table was created, print a success message
    # If the meta IS none, print an error message
    # If the file already exists, print an error message
    if meta and _filesystem.create_file(file_path):
        print('Table ' + table_name + ' created.')
        _filesystem.write_line(meta, file_path, echo=False)
    else:
        if not meta:
            print('!Failed to create table ' + table_name + ' because the provided metadata ' + data + ' is invalid.')
        else:
            print('!Failed to create table ' + table_name + ' because it already exists.')


# METHOD:       drop_table()
# DESCRIPTION:  Deletes a table within the database
# ARGUMENTS:    arguments - the list of argument strings
# RETURNS:      N/A
def drop_table(arguments):
    # Guard clause that aborts if no database is being used
    if _globals.active_db is None:
        print("!Failed because no database is being used.")
        return

    # table_name - the name of the table taken from the arguments
    # args_list - the remaining arguments without the first argument
    table_name, _ = _utils.pop_argument(arguments)
    file_path = tbl_path(table_name)

    if _filesystem.delete_file(file_path):
        print("Table " + table_name + " deleted.")
    else:
        print('!Failed to delete database ' + table_name + ' because it does not exist.')


# METHOD:       read_table()
# DESCRIPTION:  Reads in a table within the database
# ARGUMENTS:    arguments - the list of argument strings
# RETURNS:      N/A
def read_table(arguments):
    # First guard close aborts if no database is being used
    # Second guard clause aborts if the input is None
    if _globals.active_db is None:
        print("!Failed because no database is being used.")
        return
    if arguments is None:
        logging.error("Arguments in READ_TABLE are null!")
        return

    # table_name - the name of the table to be read
    # path - the path to the table file in the database's folder
    table_name, _ = _utils.pop_argument(arguments)
    path = tbl_path(table_name)

    # Prints the file's contents to the console line by line
    for line in _filesystem.read_file(path):
        print(line)

# endregion

# region UTILITY


# METHOD:       tbl_path()
# DESCRIPTION:  Utility method for creating a path that points to a table file within the current database folder
# ARGUMENTS:    name - the name of the table to assemble a path to
# RETURNS:      A string representing the path assembled from the table name
def tbl_path(name):
    return _filesystem.rpath(_globals.DATABASES_DIRECTORY, _globals.active_db, name + _globals.TABLE_FILE_TYPE)


# METHOD:       tbl_path()
# DESCRIPTION:  Utility method for creating a path that points to a database folder
# ARGUMENTS:    name - the name of the database to assemble a path to
# RETURNS:      A string representing the path assembled from the database name
def db_path(name):
    return _filesystem.rpath(_globals.DATABASES_DIRECTORY, _globals.active_db, name)


# endregion

# METHOD:       db_init()
# DESCRIPTION:  Initializes the database global variables used by the program
# ARGUMENTS:    N/A
# RETURNS:      N/A
def db_init():
    _globals.DATABASES_DIRECTORY = 'Databases'
    _globals.TABLE_FILE_TYPE = '.tbl'
