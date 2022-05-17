# FILE NAME:    _INPUT.PY
# MODULE NAME:  Input
# DESCRIPTION:  Provides methods for receiving input
# AUTHOR:       HOLDEN BOWMAN
# DATE:         MAY 7, 2022

import logging
import re
import _globals as _gl
import _dbmanagement as _db
import _utils as _ut
import _tablemanagement as _tm

# region INPUT

# REGION:       INPUT
# DESCRIPTION:  Provides methods for taking in user input

# --------- METHODS --------- #


# METHOD:       preprocess_file_input()
# DESCRIPTION:  Preprocesses the lines of the file into commands readable
#               by the program's parser
# ARGUMENTS:    file_name - the path of the specified file
# RETURNS:      N/A
def preprocess_file_input(file_name):
    # commands - the list of processed commands
    commands = []

    logging.info('Adding commands..\n')

    # Reads each line in the file and preprocesses each line
    # cur_com - the current command being assembled by the preprocessor loop
    # Ignore each line starting with '--'
    # If the line does not end with a ';' we append it to cur_com
    # If the line does end with a ';' we add it to the list of commands and reset cur_com to ''
    # Strips each line of whitespace characters
    with open(file_name, 'r') as f:
        cur_com = ''
        for line in f.readlines():
            if line.startswith('--') or line.isspace():
                continue
            else:
                cur_com += f" {line.split('--', 1)[0].strip()}"
                if cur_com.endswith(';') or '.EXIT' in cur_com.upper():
                    logging.info(f'Adding commands: {cur_com}')
                    commands.append(cur_com.strip())
                    cur_com = ''

    return commands


# METHOD:       file_input()
# DESCRIPTION:  Takes input from a specified file
# ARGUMENTS:    file_name - the path of the specified file
# RETURNS:      N/A
def file_input(file_name):
    # Preprocesses the file into lines of input usable by the parser
    commands = preprocess_file_input(file_name)

    # Executes each command in the list of commands in the file
    # Returns false if the parser returns false (on .EXIT)
    for com in commands:
        logging.info(f'Performing commands: {com}')
        if not parse(com.rstrip(';')):
            return False

    return True


# METHOD:       terminal_input()
# DESCRIPTION:  Takes in input from the terminal
# ARGUMENTS:    N/A
# RETURNS:      N/A
def terminal_input():
    # Provides input from the user until parse() returns false
    while True:
        if not parse(input()):
            break


# endregion

# region ARGUMENT HANDLING

# REGION:       ARGUMENT HANDLING
# DESCRIPTION:  Provides methods for parsing through the arguments input given to the program

# --------- METHODS --------- #


# METHOD:       parse()
# DESCRIPTION:  Parses the initial argument list
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      N/A
def parse(arguments):
    # Guard clause that aborts if the input is None
    if arguments is None:
        logging.error('Input to parser is null!')
        return

    logging.info('Parsing...')

    # arg - first argument from the arguments list
    # args - the argument new list without the first argument
    # arg is converted into upper case for the purposes of pattern matching
    arg, args = _ut.pop_argument(split_arguments(arguments))
    arg = arg.upper() if isinstance(arg, str) else ''

    logging.info(f'PARSE passed argument {arg}')

    # Match the first argument to a method call
    match arg:
        case 'CREATE':
            create(args)
        case 'DROP':
            drop(args)
        case 'USE':
            use(args)
        case 'SELECT':
            select(args)
        case 'ALTER':
            alter(args)
        case 'INSERT':
            insert(args)
        case 'UPDATE':
            update(args)
        case 'DELETE':
            delete(args)
        case 'BEGIN':
            begin(args)
        case 'COMMIT':
            commit()
        case 'READ':
            read(args)
        case '.EXIT':
            return False
        case '':
            print('ERROR: No arguments provided')
        case _:
            print('ERROR: Unrecognized argument "' + arg + '"')

    return True


# METHOD:       create()
# DESCRIPTION:  Parses the argument list after the CREATE argument
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      N/A
def create(arguments):
    # Guard clause that aborts if the input is None
    if arguments is None:
        logging.error('Arguments in CREATE are null!')
        return

    logging.info('Creating...')

    # arg - first argument from the arguments list
    # args - the argument new list without the first argument
    # arg is converted into upper case for the purposes of pattern matching
    arg, args = _ut.pop_argument(arguments)
    arg = arg.upper() if isinstance(arg, str) else ''

    logging.info(f'CREATE passed argument {arg}')

    # Match the first argument to a method call
    match arg:
        case 'DATABASE':
            _db.create_database(args)
        case 'TABLE':
            _db.create_table(args)
        case '':
            print('ERROR: Missing arguments after CREATE')
        case _:
            print('ERROR: Unrecognized argument "' + arg + '" after CREATE')


# METHOD:       drop()
# DESCRIPTION:  Parses the argument list after the DROP argument
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      N/A
def drop(arguments):
    # Guard clause that aborts if the input is None
    if arguments is None:
        logging.error('Arguments in DROP are null!')
        return

    logging.info('Dropping...')

    # arg - first argument from the arguments list
    # args - the argument new list without the first argument
    # arg is converted into upper case for the purposes of pattern matching
    arg, args = _ut.pop_argument(arguments)
    arg = arg.upper() if isinstance(arg, str) else ''

    logging.info(f'DROP passed argument {arg}')

    # Match the first argument to a method call
    match arg:
        case 'DATABASE':
            _db.drop_database(args)
        case 'TABLE':
            _db.drop_table(args)
        case '':
            print('ERROR: Missing arguments after DROP')
        case _:
            print('ERROR: Unrecognized argument "' + arg + '" after DROP')


# METHOD:       use()
# DESCRIPTION:  Parses the argument list after the USE argument
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      N/A
def use(arguments):
    # Guard clause that aborts if the input is None
    if arguments is None:
        logging.error('Arguments in USE are null!')
        print('ERROR: No database was specified')
        return

    logging.info("Using...")

    # arg - first argument from the arguments list
    # The remaining arguments in the list are ignored
    arg, _ = _ut.pop_argument(arguments)

    _db.use_database(arg)


# METHOD:       select()
# DESCRIPTION:  Parses the argument list after the SELECT argument
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      N/A
def select(arguments):

    if _gl.active_db is None:
        print("!Failed because no database is being used.")
        return
    if arguments is None:
        logging.error('Arguments in SELECT are null!')
        return

    _tm.select_records(arguments)


# METHOD:       alter()
# DESCRIPTION:  Parses the argument list after the ALTER argument
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      N/A
def alter(arguments):
    # First guard close aborts if no database is being used
    # Second guard clause aborts if the input is None
    if _gl.active_db is None:
        print("!Failed because no database is being used.")
        return
    if arguments is None:
        logging.error('Arguments in ALTER are null!')
        return

    # arg - first argument from the arguments list
    # args - the argument new list without the first argument
    arg, args = _ut.pop_argument(arguments)

    # Match the first argument to a method call
    match arg:
        case 'TABLE':
            _db.alter_table(args)
        case _:
            print('ERROR: Unrecognized argument "' + arg + '" after ALTER')


# METHOD:       insert()
# DESCRIPTION:  Parses the argument list after the INSERT argument
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      N/A
def insert(arguments):
    # First guard close aborts if no database is being used
    # Second guard clause aborts if the input is None
    if _gl.active_db is None:
        print("!Failed because no database is being used.")
        return
    if arguments is None:
        logging.error('Arguments in USE are null!')
        print('ERROR: No database was specified')
        return

    logging.info('Inserting...')

    # arg - first argument from the arguments list
    # args - the argument new list without the first argument
    # arg is converted into upper case for the purposes of pattern matching
    arg, args = _ut.pop_argument(arguments)
    arg = arg.upper()

    # Match the first argument to a method call
    match arg:
        case 'INTO':
            _tm.add_record(args)
        case _:
            print(f'Unrecognized argument {arg} after INSERT')


# METHOD:       update()
# DESCRIPTION:  Parses the argument list after the UPDATE argument
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      N/A
def update(arguments):
    # First guard close aborts if no database is being used
    # Second guard clause aborts if the input is None
    if _gl.active_db is None:
        print("!Failed because no database is being used.")
        return
    if arguments is None:
        logging.error('Arguments in USE are null!')
        print('ERROR: No database was specified')
        return

    logging.info('Updating...')

    _tm.update_records(arguments)


# METHOD:       delete()
# DESCRIPTION:  Parses the argument list after the DELETE argument
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      N/A
def delete(arguments):
    # First guard close aborts if no database is being used
    # Second guard clause aborts if the input is None
    if _gl.active_db is None:
        print("!Failed because no database is being used.")
        return
    if arguments is None:
        logging.error('Arguments in USE are null!')
        print('ERROR: No database was specified')
        return

    logging.info('Deleting...')

    _tm.delete_records(arguments)


# METHOD:       begin()
# DESCRIPTION:  Parses the argument list after the BEGIN argument
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      N/A
def begin(arguments):
    # First guard close aborts if no database is being used
    # Second guard clause aborts if the input is None
    if _gl.active_db is None:
        print("!Failed because no database is being used.")
        return
    if arguments is None:
        logging.error('Arguments in USE are null!')
        print('ERROR: No database was specified')
        return

    arg, args = _ut.pop_argument(arguments)
    arg = arg.upper()

    match arg:
        case 'TRANSACTION':
            _tm.begin_transaction()
        case _:
            print(f'ERROR: Invalid argument "{arg}" after.')


# METHOD:       commit()
# DESCRIPTION:  Commits changes to disk
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      N/A
def commit():
    # First guard close aborts if no database is being used
    # Second guard clause aborts if the input is None
    if _gl.active_db is None:
        print("!Failed because no database is being used.")
        return

    _tm.commit_transaction()


# METHOD:       read()
# DESCRIPTION:  Parses the argument list after the READ argument
# ARGUMENTS:    arguments - the list of arguments
# RETURNS:      N/A
def read(arguments):
    # Guard clause that checks for input as None and aborts
    if arguments is None:
        logging.error('Arguments in USE are null!')
        print('ERROR: No database was specified')
        return

    # Gets the file name from the arguments
    file, _ = _ut.pop_argument(arguments)

    file_input(file)

# endregion

# region UTILITY

# REGION:       UTILITY
# DESCRIPTION:  The utility section provide easy to use methods that reduce
#               the overall amount of code required for repetitive tasks and
#               allow for much cleaner code.

# --------- METHODS --------- #


# METHOD:       split_arguments()
# DESCRIPTION:  Uses a regular expression to break an input string into a list of args
# ARGUMENTS:    arguments - the input string of arguments
# RETURNS:      A list of arguments
def split_arguments(arguments: str):
    stripped = arguments.split(';', 1)[0]
    arg_list = re.findall(r'(?:VALUES|values)\s*\([\s\S]+\)|\([\s\S]+\)|\w*\.*\w+|\*|[<>=!]+|\'\w+\'', stripped)
    arguments = [x.upper() if x.upper() in _gl.KEYWORDS else x for x in arg_list]
    return arguments

# endregion
