"""
Clients should call this utility script rather than the import_manager to fetch the import status
"""

import sys
import json
from constants import RESPONSE_FIELD_STATUS, RESPONSE_FIELD_RESULT
from constants import STATUS_FAILURE
from import_manager import get_import_status


response = None

try:
    import_status = get_import_status(sys.argv[1])
    response = {
        RESPONSE_FIELD_STATUS: import_status.status,
        RESPONSE_FIELD_RESULT: import_status.result
    }
except:
    error_msg = 'An error occurred'
    print error_msg
    response = {
        RESPONSE_FIELD_STATUS: STATUS_FAILURE,
        RESPONSE_FIELD_RESULT: error_msg
    }

print json.dumps(response)
