"""
Clients should call this script rather than the import_manager
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

print json.dump(response)
