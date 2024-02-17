import sys
import json
import traceback
from jupyter_client import KernelManager

def execute_code(code):
    kc = KernelManager()
    kc.start_kernel()
    kc_client = kc.client()
    kc_client.start_channels()

    kc_client.wait_for_ready(timeout=60)

    msg_id = kc_client.execute(code)

    outputs=[]

    while True:
        msg = kc_client.get_iopub_msg()
        if msg['parent_header'].get('msg_id') == msg_id:
            msg_type = msg['msg_type']
            if msg_type == 'stream':
                outputs.append(msg['content']['text'])
            elif msg_type == 'display_data':
                data = msg['content']['data']
                if 'text/plain' in data:
                    outputs.append(data['text/plain'])
            elif msg_type == 'execute_result':
                data = msg['content']['data']
                if 'text/plain' in data:
                    outputs.append(data['text/plain'])
            elif msg_type == 'status' and msg['content']['execution_state'] == 'idle':
                break
    return outputs



try:

    with open('generated_code.py', 'r') as f:
        input_code = f.read()

    output = execute_code(input_code)
    
    result = {'output': output}
    print(json.dumps(result))
except Exception as e:
    error = {'error': str(e), 'traceback': traceback.format_exc()}
    print(json.dumps(error))

