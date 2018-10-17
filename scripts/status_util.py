"""
Clients should call this utility script rather than the import_manager to fetch the import status
"""

import sys
import json
from constants import RESPONSE_FIELD_STATUS, RESPONSE_FIELD_RESULT, RESPONSE_FIELD_STATUS_CODE
from constants import STATUS_CODE_OK, STATUS_CODE_ERROR, STATUS_CODE_BAD_REQUEST
from import_manager import get_import_status

response = None

try:
    if len(sys.argv) < 2:
        response = {
            RESPONSE_FIELD_STATUS_CODE: STATUS_CODE_BAD_REQUEST,
            RESPONSE_FIELD_RESULT: "Import id required"
        }
    else:
        import_status = get_import_status(sys.argv[1])
        response = {
            RESPONSE_FIELD_STATUS_CODE: STATUS_CODE_OK,
            RESPONSE_FIELD_STATUS: import_status.status,
            RESPONSE_FIELD_RESULT: str(import_status.result)
        }
except Exception:
    response = {
        RESPONSE_FIELD_STATUS_CODE: STATUS_CODE_ERROR,
        RESPONSE_FIELD_RESULT: 'An error occurred'
    }

print json.dumps(response)
