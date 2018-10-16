"""
Clients should call this utility script rather than the import_manager to import a csv
"""

import sys
import json
from constants import RESPONSE_FIELD_ID, RESPONSE_FIELD_STATUS, RESPONSE_FIELD_RESULT
from constants import STATUS_SUCCESS, STATUS_FAILURE
from import_manager import import_csv, ImportInProgressError


def generate_error_response(error_msg):
    print error_msg
    return {
        RESPONSE_FIELD_STATUS: STATUS_FAILURE,
        RESPONSE_FIELD_RESULT: error_msg
    }


response = None

try:
    task_id = import_csv(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    response = {
        RESPONSE_FIELD_STATUS: STATUS_SUCCESS,
        RESPONSE_FIELD_ID: task_id
    }
except ImportInProgressError:
    response = generate_error_response('There is already an import in progress for the country')
except:
    response = generate_error_response('An error occurred')

print json.dumps(response)

