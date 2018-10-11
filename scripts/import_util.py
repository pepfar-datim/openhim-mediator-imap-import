"""
Clients should call this utility script rather than the import_manager to import a csv
"""

import sys
import json
from constants import RESPONSE_FIELD_ID
from import_manager import import_csv


task_id = import_csv('', sys.argv[1], sys.argv[2], sys.argv[3])
response = {
    RESPONSE_FIELD_ID: task_id
}

print json.dumps(response)

