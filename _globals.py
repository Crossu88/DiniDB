# FILE NAME:    _GLOBALS.PY
# MODULE NAME:  Globals
# DESCRIPTION:  Contains the global variables used across the program
# AUTHOR:       HOLDEN BOWMAN
# DATE:         MAY 7, 2022

# region GLOBALS

# REGION:       GLOBALS
# DESCRIPTION:  Contains global variables used in the program

# Runtime Constants Variables
CURRENT_DIRECTORY = ''
DATABASES_DIRECTORY = ''
TABLE_FILE_TYPE = ''

KEYWORDS = []

# Globals Variables
active_db = None

# endregion


# METHOD:       gl_init()
# DESCRIPTION:  Initializes the global variables used by the program
# ARGUMENTS:    N/A
# RETURNS:      N/A
def gl_init():
    # --------- FILESYSTEM --------- #

    # Global Constants
    global CURRENT_DIRECTORY
    CURRENT_DIRECTORY = ''

    # --------- DB MANAGER --------- #

    # Global Constants
    global DATABASES_DIRECTORY
    DATABASES_DIRECTORY = ''
    global TABLE_FILE_TYPE
    TABLE_FILE_TYPE = ''
    global KEYWORDS
    KEYWORDS = ['CREATE', 'DROP', 'DATABASE', 'TABLE', 'USE', 'ALTER', 'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO',
                'VALUES', 'UPDATE', 'SET', 'DELETE', 'ON', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'JOIN', 'BEGIN',
                'COMMIT', 'COUNT', 'AVG', 'MAX', 'MIN']

    # Globals Variables
    global active_db
    active_db = None
