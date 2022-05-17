import re
import _globals as _gl

# region UTILITY

# REGION:       UTILITY
# DESCRIPTION:  The utility section provide easy to use methods that reduce
#               the overall amount of code required for repetitive tasks and
#               allow for much cleaner code.

# --------- METHODS --------- #


# METHOD:       pop_arguments()
# DESCRIPTION:  Splits a list of arguments into the first argument and a list of the remaining args
# ARGUMENTS:    arguments - a list of strings representing the arguments being parsed through
# RETURNS:      A two element tuple where element one is the first argument in the list
#               and element two is the remaining arguments in the list without element one
def pop_argument(arguments):
    if arguments is None or arguments == []:
        return None, []
    if isinstance(arguments, str):
        return arguments, []
    else:
        return arguments[0], remove_first_arg(arguments)


# METHOD:       remove_first_arg()
# DESCRIPTION:  Removes the first argument from a list of args
# ARGUMENTS:    table - a list of arguments
# RETURNS:      The list of arguments without the first argument
def remove_first_arg(table):
    return remove_arg(table, table[0]) if table is not None else None


# METHOD:       remove_arg()
# DESCRIPTION:  Removes a specified argument at an element index using a list generator
# ARGUMENTS:    table - a list of arguments
#               element - index of the argument to remove
# RETURNS:      The argument list without the specified argument OR the last remaining argument
def remove_arg(table, element):
    # Guard clause that aborts for empty lists
    if len(table) <= 1:
        return None

    # The list of arguments without the specified argument
    # Uses a list generator to create a new list
    new_args = [x for x in table if x != element]  # List generator that creates a new list without the element

    # Returns the remaining arguments if the list has more than one argument remaining
    # Otherwise, return the last element of the list
    return new_args if len(new_args) > 1 else new_args[0]

# endregion
