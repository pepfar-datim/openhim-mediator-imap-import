"""
Clients should call this utility script rather than the import_manager to fetch the import status
"""

import sys
import json
from constants import RESPONSE_FIELD_STATUS, RESPONSE_FIELD_RESULT
from import_manager import get_import_status


import_status = get_import_status(sys.argv[1])
response = {
    RESPONSE_FIELD_STATUS: import_status.status,
    RESPONSE_FIELD_RESULT: import_status.result
}

print json.dumps(response)
