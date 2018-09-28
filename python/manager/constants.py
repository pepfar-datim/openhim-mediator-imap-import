ENV_CELERY_CONFIG = 'celery_config'

TASK_ID_KEY = 'id'
TASK_ID_SEPARATOR = '-'

RESPONSE_FIELD_ID = 'id'
RESPONSE_FIELD_STATUS = 'status'
RESPONSE_FIELD_RESULT = 'result'


# TODO Use an enum for exit codes
"""
0, 1, 2 are reserved based on conventions where 0 is success, 
1 is errors in the script, 2 wrong command usage
"""
EXIT_CODE_IMPORT_IN_PROGRESS = 3
EXIT_CODE_INVALID_IMPORT = 4
