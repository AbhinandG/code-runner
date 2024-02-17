import requests
import tempfile
import os
import json
import re
from io import StringIO
import sys

def run_code(input_code):
    temp_file = tempfile.NamedTemporaryFile(suffix='.py', delete=False)
    temp_file.write(input_code.encode())
    temp_file.close()
    stdout = sys.stdout
    sys.stdout = StringIO()
    output = ''
    return_code = None
    try:
        exec(compile(open(temp_file.name).read(), temp_file.name, 'exec'), globals())
        output = sys.stdout.getvalue()
    except Exception as e:
        output = str(e)
        return_code = 1
    else:
        return_code = 0
    sys.stdout = stdout
    os.remove(temp_file.name)
    return output, return_code
