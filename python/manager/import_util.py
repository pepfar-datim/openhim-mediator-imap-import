"""
Clients should call functions in this module rather than the import_manager
"""

import json
from constants import RESPONSE_FIELD_ID, RESPONSE_FIELD_STATUS, RESPONSE_FIELD_RESULT
from import_manager import import_csv, get_import_status


def import_csv(script_filename, csv, country_code, period):
    task_id = import_csv(script_filename, csv, country_code, period)
    response = {
        RESPONSE_FIELD_ID: task_id
    }

    print json.dump(response)


def get_import_status(import_id):
    import_status = get_import_status(import_id)
    response = {
        RESPONSE_FIELD_STATUS: import_status.status,
        RESPONSE_FIELD_RESULT: import_status.result
    }

    print json.dump(response)

