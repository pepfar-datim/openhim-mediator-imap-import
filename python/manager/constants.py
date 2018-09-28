ENV_CELERY_CONFIG = 'celery_config'

TASK_ID_KEY = 'id'
TASK_ID_SEPARATOR = '-'

# TODO Use an enum for exit codes, client code should interprete 0 as normal termination
"""
0, 1, 2 are reserved based on conventions where 0 is success, 
1 is errors in the script, 2 wrong command usage
"""
ERROR_IMPORT_IN_PROGRESS = 3
ERROR_INVALID = 4
