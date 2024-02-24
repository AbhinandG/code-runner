import socket
from jupyter_client import KernelManager

# Create a socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 5555))
server_socket.listen(1)
# Start kernel
kc = KernelManager()
kc.start_kernel()
kc_client = kc.client()
kc_client.start_channels()

print("Socket server listening on port 5555...")

try:
    while True:  
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr} established.")

        while True:  
            kc_client.wait_for_ready(timeout=60)

            message = client_socket.recv(1024)
            if not message:
                break
            print(f"Received: {message}")
            
            code_to_execute = message.decode()
            print(f"Executing: {code_to_execute}")
            msg_id = kc_client.execute(code_to_execute)

            outputs = []

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

            print(outputs)
            client_socket.sendall(str(outputs).encode())

except Exception as e:
    print("An error occurred:", e)

finally:
    kc_client.stop_channels()
    kc.shutdown_kernel()
