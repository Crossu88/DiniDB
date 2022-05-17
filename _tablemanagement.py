# FILE NAME:    _TABLEMANAGEMENT.PY
# MODULE NAME:  Table Management
# DESCRIPTION:  Provides methods for managing the data within tables
# AUTHOR:       HOLDEN BOWMAN
# DATE:         MAY 7, 2022
import logging
import os
import re
import sys
from dataclasses import dataclass, field
import _dbmanagement as _db
import _utils as _ut
import _filesystem as _fs
import _globals as _gl

# Internal global variables
transaction_active = False
transaction_key = ''
transaction = []

# region CLASSES

# REGION:       CLASSES
# DESCRIPTION:  Contains the classes used to represent Tables and Records in the database

# --------- CLASS DEFINITIONS --------- #


# TableLocked Class
#
# Description:
# When a table is locked, this exception will be raised
class TableLockedError(Exception):
    pass


# Record Class
#
# Description:
# The Record class inherits from the 'dict' class. It's effectively a dictionary with a dot operator.
class Record(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


# Table Class
#
# Member Variables:
# path:     The path of the table's file in the database
# schema:   The metadata string of the table
# types:    The data types of each element in the record
# fields:   The list of strings representing the field name of each element in the record
# records:  The list of dictionaries that represent each record
#
# Description:
# The Table class represent tables in their logical form when loaded into the program.
# This is used by the program to store useful information about the table and allow for
# the table to be easily modified before it is written back to the file.

@dataclass
class Table:
    path: str
    schema: str = field(default_factory=str)
    types: list[str] = field(default_factory=list)
    fields: list[str] = field(default_factory=list)
    records: list[Record[str, str]] = field(default_factory=list)

    # Represents the table when printed as a string
    def __str__(self) -> str:
        # Formats the member variables of the table into lines
        self_str = f'Path: "{self.path}"\n' \
                   f'Schema: "{self.schema}"\n' \
                   f'Types: {self.types}\n' \
                   f'Fields: {self.fields}\n' \
                   f'Records: '

        # If there are no records, represent the records as an empty list
        if len(self.records) < 1:
            return self_str + 'Records: []'

        # If records exist, start building the records string
        records_str = '[\n'

        # For each record in the records list, add them to the records string
        for rec in self.records:
            records_str += f'\t{rec}\n'

        # Close off the records string
        records_str += ']'

        # Add the records string to the string representing the table
        self_str += records_str

        return self_str

    # After the path has been set for the table, initialize the table's member variables
    def __post_init__(self) -> None:
        # Return an uninitialized table if the path is not set
        if self.path is None:
            return

        data = []

        # Attempt to read the file specified by the table's file path
        try:
            # data - The lines read from the table file
            data = open(self.path, 'r').readlines()
        except FileNotFoundError as err:
            logging.error(f'ERROR: Attempt was made to create a table from the nonexistent file {self.path}')
            raise err

        if len(data) < 1:
            return

        # remove lock string if the table is locked
        if data[0].startswith('&'):
            data.remove(data[0])

        # meta - The metadata of the table
        # lines - the records of the table in their string representation
        meta = data[0].strip()
        lines = data[1:]

        # Since the meta variable already contains the metadata, assign the schema of the table
        self.schema = meta

        # Reads in the field names from the metadata of the table and turns them into a list
        # of strings that act as their keys in the dictionaries that represent each record.
        # This is done by using a regular expression to extract the variable names from the
        # metadata string.
        self.fields = re.findall(r'\w+(?=\s\w+)', meta)

        # Reads in the datatypes from the metadata of the table and convert them into strings
        # representing their types in python. This is done by using a regular expression to
        # extract the types from the metadata string to create a list of data types. Then, a
        # list generator is used to create a list of the datatypes. Any type with varchar is
        # replaced by the str datatype for use in python.
        self.types = [x.replace('varchar', 'str') for x in re.findall(r'(?!\w+\s)(?:int|varchar|float)', meta)]

        # Converts each record's string representation as read from the table's file into a
        # dictionary that represents each of the records. This is done by splitting the record's
        # string representation using the split() function to get the values of each field
        for line in lines:
            if line.startswith('&'):
                continue

            record_strings = line.strip().split('|')

            # Converts all members of the record to their equivalent types in python.
            record_dict = Record({self.fields[i]: eval(f'{self.types[i]}("{record_strings[i]}")')
                                  for i in range(len(self.fields))})

            self.records.append(record_dict)


# endregion

# region TABLE CLASS OPERATIONS

# REGION:       TABLE CLASS OPERATIONS
# DESCRIPTION:  Provides helpful functions for using the Table class

# --------- METHODS --------- #


# METHOD:       format_record()
# DESCRIPTION:  Formats a record into a string
# ARGUMENTS:    record - the name of the table to retrieve
# RETURNS:      A string representation of the record
def format_record(record: Record) -> str:
    return '|'.join([str(x) for x in record.values()])


# METHOD:       format_records()
# DESCRIPTION:  Formats a list of records
# ARGUMENTS:    records - the list of Record objects to format
# RETURNS:      A list of Records in their string representations
def format_records(records: list[Record]) -> list[str]:
    formatted_records = []

    for record in records:
        formatted_records.append(format_record(record))

    return formatted_records


# METHOD:       format_records()
# DESCRIPTION:  Formats a list of records
# ARGUMENTS:    records - the list of Record objects to format
# RETURNS:      A list of Records in their string representations
def filter_table(table: Table, fields: list[str], condition: str = 'True') -> Table:
    # Make a copy of the table
    new_table = Table(None)

    # Filter out the types of each field by removing all
    # field type elements for each of the field name elements
    # that are not in the fields parameter
    new_table.types = [table.types[x] for x in range(len(new_table.types)) if table.fields[x] in fields]

    # Filter the fields and remove all fields not within the fields parameter
    new_table.fields = [x for x in table.fields if x in fields]

    # Filter the records and remove all dictionary keys that are not in the fields parameter
    new_table.records = [Record({k: v for (k, v) in x.items() if k in fields})
                         for x in table.records
                         if eval(condition, {}, dict(x))]

    # Filters out the schema of the list by using list comprehension hackery
    new_table.schema = '|'.join([[y for y in table.schema.split('|') if x in y][0] for x in fields])

    return new_table


# METHOD:       retrieve_table()
# DESCRIPTION:  Retrieves a table as an instance of the Table class
# ARGUMENTS:    name - the name of the table to retrieve
# RETURNS:      A table object representing the specified table
def retrieve_table(name: str, block_on_locked: bool = True) -> Table:
    table = Table(_db.tbl_path(name))

    if not _db.validate_table(name):
        print(f'!Failed because {name} does not exist')
        return Table(None)

    if block_on_locked:
        try:
            acquire_lock(name)
        except TableLockedError:
            print(f'Error: Table {name} is locked!')
            raise TableLockedError

    return table


# METHOD:       write_table()
# DESCRIPTION:  Writes a table to memory
# ARGUMENTS:    table - the table to write to memory
# RETURNS:      N/A
def write_table(table: Table):
    with open(table.path, 'w') as f:
        f.write(f'{table.schema}\n')
        for record in table.records:
            f.write(f'{format_record(record)}\n')
        f.close()


# METHOD:       combine_tables()
# DESCRIPTION:  Combines two tables to create a table with the schema, types, and field combined
#               Holds no records from either table
# ARGUMENTS:    table1 - the first table to combine
#               table2 - the second table to combine
# RETURNS:      The newly combined table
def combine_tables(table1: Table, table2: Table) -> Table:
    # Instantiates a blank table
    new_table = Table(None)

    # Combines the schemas
    new_table.schema = f'{table1.schema}|{table2.schema}'

    # Combines the 'types' lists
    new_table.types = table1.types + table2.types

    # Combines the 'fields' lists
    new_table.fields = table1.fields + table2.fields

    return new_table


# METHOD:       inner_join()
# DESCRIPTION:  Performs an inner join operation on two tables
# ARGUMENTS:    table_tup1 - A tuple of a name that represents a table and the table being represented
#               table_tup2 - A tuple of a name that represents a table and the table being represented
#               condition - the condition to evaluate as a string
# RETURNS:      A joined table
def inner_join(table_tup1: tuple[str, Table], table_tup2: tuple[str, Table], condition: str) -> Table:
    # The tables to be joined and their identifiers
    left_name = table_tup1[0]
    left_table = table_tup1[1]

    right_name = table_tup2[0]
    right_table = table_tup2[1]

    # Combine the table schemas, fields and types
    new_table = combine_tables(left_table, right_table)

    # Create a list containing lists of records where the condition was satisfied
    nested_records = [[l_rec | r_rec for r_rec in right_table.records
                       if eval(condition, {}, {left_name: l_rec, right_name: r_rec})]
                      for l_rec in left_table.records]

    # Flatten out the nested records by using list comprehension
    new_table.records = [record for nested_record in nested_records for record in nested_record]

    return new_table


# METHOD:       left_outer_join()
# DESCRIPTION:  Performs a left outer join operation on two tables
# ARGUMENTS:    table_tup1 - A tuple of a name that represents a table and the table being represented
#               table_tup2 - A tuple of a name that represents a table and the table being represented
#               condition - the condition to evaluate as a string
# RETURNS:      N/A
def left_outer_join(table_tup1: tuple[str, Table], table_tup2: tuple[str, Table], condition: str):
    # The tables to be joined
    left_table = table_tup1[1]
    right_table = table_tup2[1]

    # Perform an inner join to get the intersecting elements in the join
    new_table = inner_join(table_tup1, table_tup2, condition)

    # Create an empty dictionary for any records that don't find a match
    right_empty_dict = {x: '' for x in right_table.fields}

    # Check each record in the left table to see if it was found in the
    # table created from the inner join. If the record was not found,
    # append it to the list of dictionaries with the fields from the
    # right dictionary set to empty.
    for left_record in left_table.records:
        found = False
        for new_record in new_table.records:
            if all(x in new_record.items() for x in left_record.items()):
                found = True
                break
        if not found:
            new_table.records.append(Record(left_record | right_empty_dict))

    return new_table


# METHOD:       right_outer_join()
# DESCRIPTION:  Performs a right outer join operation on two tables
# ARGUMENTS:    table_tup1 - A tuple of a name that represents a table and the table being represented
#               table_tup2 - A tuple of a name that represents a table and the table being represented
#               condition - the condition to evaluate as a string
# RETURNS:      N/A
def right_outer_join(table_tup1: tuple[str, Table], table_tup2: tuple[str, Table], condition: str):
    # The tables to be joined
    left_table = table_tup1[1]
    right_table = table_tup2[1]

    # Perform an inner join to get the intersecting elements in the join
    new_table = inner_join(table_tup1, table_tup2, condition)

    # Create an empty dictionary for any records that don't find a match
    left_empty_dict = {x: '' for x in left_table.fields}

    # Check each record in the right table to see if it was found in the
    # table created from the inner join. If the record was not found,
    # append it to the list of dictionaries with the fields from the
    # right dictionary set to empty.
    for right_record in right_table.records:
        found = False
        for new_record in new_table.records:
            if all(x in new_record.items() for x in right_record.items()):
                found = True
                break
        if not found:
            new_table.records.append(Record(left_empty_dict | right_record))

    return new_table


# METHOD:       find_max()
# DESCRIPTION:  Performs a right outer join operation on two tables
# ARGUMENTS:    table - The table to find the max from
#               key - The field to find the max from
# RETURNS:      N/A
def find_max(table: Table, key: str):
    nums = []

    for record in table.records:
        nums.append(record[key.strip('()')])

    return max(nums)


# METHOD:       find_min()
# DESCRIPTION:  Performs a right outer join operation on two tables
# ARGUMENTS:    table - The table to find the min from
#               key - The field to find the min from
# RETURNS:      N/A
def find_min(table: Table, key: str):
    nums = []

    for record in table.records:
        nums.append(record[key.strip('()')])

    return min(nums)


# METHOD:       find_min()
# DESCRIPTION:  Performs a right outer join operation on two tables
# ARGUMENTS:    table - The table to find the min from
#               key - The field to find the min from
# RETURNS:      N/A
def find_avg(table: Table, key: str):
    nums = []

    for record in table.records:
        nums.append(record[key.strip('()')])

    return sum(nums) / len(nums)

# endregion

# region TABLE MANAGEMENT

# REGION:       TABLE MANAGEMENT
# DESCRIPTION:  Provides methods for modifying the records of tables

# --------- METHODS --------- #


# METHOD:       generate_record_string()
# DESCRIPTION:  Creates the string representing the record in the table using a regular expression
# ARGUMENTS:    The string representing the values() object
# RETURNS:      The values() object as a string
def generate_record_string(values):
    # Use a regular expression to generate a list of strings from the values() object
    data = re.findall(r'\d+(?:\.\d+)?|(?!\')[\w\d]*(?=\')', values)

    # Joins the records together into a string
    values_str = '|'.join(data)

    # Returns the string if it exists
    # Otherwise, return an empty string
    return values_str if isinstance(values_str, str) else ''


# METHOD:       add_record()
# DESCRIPTION:  Adds a record to the given table
# ARGUMENTS:    parameters - a string representing the parameters
# RETURNS:      The metadata string
def add_record(arguments):
    # table_name - the name of the table to add a record to
    table_name, args = _ut.pop_argument(arguments)
    values, _ = _ut.pop_argument(args)

    # If the table does not exist, print an error message and abort
    if not _db.validate_table(table_name):
        print(f'!Failed to insert record because table {table_name} does not exist.')
        return

    # values_str - the values() object as a string
    # table_path - the path of the table in the database's folder
    values_str = generate_record_string(values)
    table_path = _db.tbl_path(table_name)

    # Appends the new record to the end of the table file
    _fs.write_line(values_str, table_path)

    # Print a success message
    print('1 new record inserted.')


# METHOD:       select_records()
# DESCRIPTION:  Selects fields from a record that satisfy a condition
# ARGUMENTS:    arguments - the arguments passed down to the method
# RETURNS:      N/A
def select_records(arguments):
    # fields - the fields to select from the table/tables
    # from_data - the arguments that come after the 'FROM' keyword
    # table_data - the string containing table names and identifiers
    # tables - the list of tables listed as strings
    # table_names - the identifiers of the tables used to create the condition
    # condition_data - the arguments that come after the 'WHERE' or 'ON' keyword
    # condition - the condition formatted as a string to use for evaluation
    fields = combine_arguments_between(None, 'FROM', arguments)
    from_data = combine_arguments_between('FROM', 'WHERE' if 'WHERE' in arguments else 'ON', arguments)
    table_data = [x for x in from_data if x not in _gl.KEYWORDS]
    tables = table_data[::2]
    table_names = table_data[1::2]
    condition_data = combine_arguments_between('WHERE' if 'WHERE' in arguments else 'ON', None, arguments)
    condition = format_condition(condition_data) if 'WHERE' in arguments or 'ON' in arguments else 'True'

    # Checks the arguments to see if there are an invalid number of tables and table identifiers
    if len(tables) > 1 and len(tables) != len(table_names) or len(tables) > 2:
        logging.error('ERROR: Invalid number of arguments provided after FROM')

    # Initialize a blank table
    selected_table = Table(None)

    # Check the arguments to see what operations are being done on the table/tables
    if 'JOIN' in arguments or len(tables) > 1:
        # If we are performing a join, then set up the tables and identifiers as a tuple to
        # pass as an argument to the join methods
        table_tup1 = (table_names[0], retrieve_table(tables[0], False))
        table_tup2 = (table_names[1], retrieve_table(tables[1], False))
        if 'INNER' in arguments or 'WHERE' in arguments:
            selected_table = inner_join(table_tup1, table_tup2, condition)
        elif 'OUTER' in arguments:
            if 'RIGHT' in arguments:
                selected_table = right_outer_join(table_tup1, table_tup2, condition)
            elif 'LEFT' in arguments:
                selected_table = left_outer_join(table_tup1, table_tup2, condition)
        # If the condition was used for the join, set the condition to evaluate as true
        condition = 'True'
    # If there is only one table, select from that table
    elif len(tables) == 1:
        selected_table = retrieve_table(tables[0], False)

    # In the case that we are just getting the count, max,
    # min or average, get those instead of the table's record
    if 'COUNT' in fields:
        print(''.join(fields))
        print(len(selected_table.records))
        return
    if 'MAX' in fields:
        print(''.join(fields))
        print(find_max(selected_table, fields[1]))
        return
    if 'MIN' in fields:
        print(''.join(fields))
        print(find_min(selected_table, fields[1]))
        return
    if 'AVG' in fields:
        print(''.join(fields))
        print(find_avg(selected_table, fields[1]))
        return

    # If the wildcard is used, then print all fields
    if '*' in fields:
        fields = selected_table.fields

    # Filter the table to only show the fields we want
    selected_table = filter_table(selected_table, fields, condition)

    # Print the new table's schema
    print(selected_table.schema)

    # Print the new table's records
    for record in format_records(selected_table.records):
        print(record)


# METHOD:       update_records()
# DESCRIPTION:  Updates the field of a record where a condition is satisfied
# ARGUMENTS:    arguments - the arguments passed down to the method
# RETURNS:      N/A
def update_records(arguments):
    # Prevents transactions if no transaction is ongoing
    if not transaction_active:
        print(f'Error: no transaction active!')

    # table_name - the name of the table to select from
    # set_str - the string that SHOULD contain 'SET'
    # assignment_list - the assignment operation as a list of strings
    # assignment - the assignment operation on the table
    # args - the remaining list of arguments
    table_name, args = _ut.pop_argument(arguments)
    set_str, args = _ut.pop_argument(args)
    assignment_list, args = combine_arguments_before('where', args)
    assignment = ''.join(assignment_list)

    # Guard clause that aborts if the 'FROM' argument does not exist
    if 'SET' not in set_str.upper():
        logging.info('ERROR: Invalid arguments in select_records')
        return

    table = None

    try:
        # Instantiate a table object from the table file
        table = retrieve_table(table_name)
    except TableLockedError:
        abort_transaction()
        return

    # Initially set the condition to evaluate as true
    condition = 'True'

    if len(args) > 2:
        # where_str - the string the MAY contain 'WHERE'
        # cond_str - the condition following the 'WHERE' argument as a string
        # condition - the condition following the 'WHERE' argument
        # condition is by replacing single instance of '=' with '=='
        where_str, args = _ut.pop_argument(args)
        cond_str = ''.join(args)
        condition = re.sub(r'(?<![=><!])\=(?!=)', '==', cond_str)

    # mod_count - the amount of modifications made to the table
    mod_count = 0

    # Checks each record to see if the condition is met
    # If it is, perform the assignment
    for record in table.records:
        if eval(condition, {}, record):
            exec(assignment, {}, record)
            mod_count += 1

    # If mod_count == 0, print 'No records modified'
    # If mod_count == 1, print '1 record modified'
    # If mod_count  > 1, print '# records modified
    print(f'{"No" if mod_count == 0 else mod_count} record{"s" if mod_count != 1 else ""} modified.')
    # Write the table to the file

    transaction.append(table)


# METHOD:       update_records()
# DESCRIPTION:  Updates fields from a record that satisfy a condition
# ARGUMENTS:    arguments - the arguments passed down to the method
# RETURNS:      N/A
def delete_records(arguments):
    # Prevents transactions if no transaction is ongoing
    if not transaction_active:
        print(f'Error: no transaction active!')

    # table_name - the name of the table to select from
    # set_str - the string that SHOULD contain 'SET'
    # assignment_list - the assignment operation as a list of strings
    # assignment - the assignment operation on the table
    # args - the remaining list of arguments
    from_str, args = _ut.pop_argument(arguments)
    table_name, args = _ut.pop_argument(args)

    # Guard clause that aborts if the 'FROM' or 'WHERE' argument does not exist
    if 'FROM' not in from_str.upper():
        logging.info('ERROR: Invalid arguments in select_records')
        return

    # Initially set table to none
    table = None

    try:
        # Instantiate a table object from the table file
        table = retrieve_table(table_name)
    except TableLockedError:
        abort_transaction()
        return

    # Initially set the condition to evaluate as true
    condition = 'True'

    if len(args) > 2:
        # where_str - the string the MAY contain 'WHERE'
        # cond_str - the condition following the 'WHERE' argument as a string
        # condition - the condition following the 'WHERE' argument
        # condition is by replacing single instance of '=' with '=='
        where_str, args = _ut.pop_argument(args)
        cond_str = ''.join(args)
        condition = re.sub(r'(?<![=><!])\=(?!=)', '==', cond_str)

    # mod_count - the amount of modifications made to the table
    mod_count = 0

    # Checks each record to see if the condition is met
    # If it is, perform the assignment
    for record in table.records:
        if eval(condition, {}, record):
            table.records.remove(record)
            mod_count += 1

    # If mod_count == 0, print 'No records modified'
    # If mod_count == 1, print '1 record modified'
    # If mod_count  > 1, print '# records modified
    print(f'{"No" if mod_count == 0 else mod_count} record{"s" if mod_count != 1 else ""} deleted.')

    # Write the table to the file
    write_table(table)


# endregion

# region TRANSACTIONS

# REGION:       TRANSACTIONS
# DESCRIPTION:  Provides methods for performing transactions

# --------- METHODS --------- #


# METHOD:       acquire_lock()
# DESCRIPTION:  Acquires a lock for the table being used
# ARGUMENTS:    name - the name of the table
# RETURNS:      N/A
def acquire_lock(name: str):
    lines = None

    with open(_db.tbl_path(name), 'r') as f:
        lines = f.readlines()
        f.close()

    transaction_lock = lines[0]

    if transaction_lock.startswith('&') and transaction_key not in transaction_lock:
        raise TableLockedError

    with open(_db.tbl_path(name), 'w') as f:
        f.write(f'{transaction_key}\n')
        f.writelines(lines)


# METHOD:       begin_transaction()
# DESCRIPTION:  Initializes globals to begin a transaction and creates a transaction key
# ARGUMENTS:    N/A
# RETURNS:      N/A
def begin_transaction():
    global transaction_active
    global transaction_key
    global transaction

    if transaction_active:
        print(f'ERROR: Transaction is currently active!')

    transaction_active = True
    transaction_key = f'&{os.getpid()}'
    transaction = []

    print('Transaction starts.')


# METHOD:       commit_transaction()
# DESCRIPTION:  Commits transaction data to memory
# ARGUMENTS:    N/A
# RETURNS:      N/A
def commit_transaction():
    global transaction_active
    global transaction_key
    global transaction

    # Checks to see if there is anything to commit
    # If there is, print a success message
    # Otherwise, don't print anything
    if len(transaction) > 0:
        print('Transaction committed.')
        for table in transaction:
            write_table(table)

    transaction_active = False
    transaction_key = ''
    transaction = []


# METHOD:       abort_transaction()
# DESCRIPTION:  Aborts transaction and resets the globals
# ARGUMENTS:    N/A
# RETURNS:      N/A
def abort_transaction():
    global transaction_active
    global transaction_key
    global transaction

    transaction_active = False
    transaction_key = ''
    transaction = []

    print('Transaction abort.')


# endregion

# region UTILITY

# REGION:       UTILITY
# DESCRIPTION:  The utility section provide easy to use methods that reduce
#               the overall amount of code required for repetitive tasks and
#               allow for much cleaner code.

# --------- METHODS --------- #


# METHOD:       combine_arguments_before()
# DESCRIPTION:  Utility method for combining all arguments that proceed a specified arguments in a list
# ARGUMENTS:    argument - the name of the argument that comes after all the elements to be combined
#               arguments - the list of arguments to combine
# RETURNS:      A tuple containing the list combined of arguments and the list of remaining arguments
def combine_arguments_before(argument: str, arguments: list):
    # comb_args - the list of combined arguments
    # new_list - a copy of the arguments list
    comb_args = []
    new_list = arguments.copy()

    # Iterate through every element to see if the argument being searched for exists
    # Combines all proceeding elements into the comb_args list
    # Removes proceeding elements from the argument list copy
    i = 0
    while argument.upper() not in arguments[i].upper() and i < len(arguments):
        comb_args.append(arguments[i])
        new_list.remove(arguments[i])
        i += 1

    # Return the combined arguments as well as the remaining arguments
    return comb_args, new_list


# METHOD:       combine_arguments_before()
# DESCRIPTION:  Utility method for combining all arguments are in between two specified arguments in a list
# ARGUMENTS:    arg1
#               arg2
#               arguments - the list of arguments to combine
# RETURNS:      A tuple containing the list of combined arguments
def combine_arguments_between(arg1: str, arg2: str, arguments: list) -> list[str]:
    index1 = 0
    index2 = len(arguments)

    if arg1 in arguments:
        index1 = arguments.index(arg1) + 1

    if arg2 in arguments:
        index2 = arguments.index(arg2)

    return arguments[index1:index2]


# METHOD:       combine_arguments_before()
# DESCRIPTION:  Formats a condition data list into a string that can be evaluated
# ARGUMENTS:    conditions_data - the list of arguments to form a condition string from
# RETURNS:      A condition formatted as a string to be evaluated
def format_condition(conditions_data: list[str]) -> str:
    # If there are no conditions to evaluate, return an empty string
    if conditions_data is not None and len(conditions_data) <= 1:
        return ''

    # Join the condition_data arguments into a single string
    # Then, replace any singular '=' with '=='
    cond_str = ''.join(conditions_data)
    condition = re.sub(r'(?<![=><!])\=(?!=)', '==', cond_str)

    return condition


# endregion
