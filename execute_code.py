import sys
import json
import traceback
import socket
from jupyter_client import KernelManager
import atexit


def send_code_to_kernel(code):
    host = '0.0.0.0'
    port = 5555  # Port used by kernel_initializer.py

    print('Going to connect....')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print('trying to connect...')
        s.connect((host, port))
        print('connected successfully!')
        s.sendall(code.encode())
        response = s.recv(1024)
        print(f"Received: {response}")
        return response


try:
    host = '0.0.0.0'  
    port = 12345  

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()

        print(f"Listening on {host}:{port}")

        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)

                data = conn.recv(1024)

                print(f"Received: {data}")

                if not data:
                    print("No data received")
                    break

                output = send_code_to_kernel(data.decode())
                print(f"Response from kernel_initializer: {output}")
                result = {'output': output.decode()}
                conn.sendall(json.dumps(result).encode())
except Exception as e:
    error = {'error': str(e), 'traceback': traceback.format_exc()}
    print(json.dumps(error))
