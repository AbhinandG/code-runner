import requests
import tempfile
import os
import json
import re
from io import StringIO
import sys
from codeRunner import run_code
import subprocess
import streamlit as st
import time
import os
import socket


def get_session_state():
    return st.session_state.setdefault('my_list', [])

my_list = get_session_state()


def update_chat_history(question, code, output):
    my_list.append({"question": question, "code": code, "output": output})

    if len(my_list) > 5:
        my_list.pop(0)  

    print(f'Chat history now has {len(my_list)} items')



def send_code_to_container(code):
    host = 'localhost'  
    port = 12345  

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(code.encode())
        response = s.recv(1024)
        return json.loads(response.decode())



def generate_code(prompt):        
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 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'
    }
    csv_files = [file for file in os.listdir('resources/file') if file.endswith('.csv')]
    
    transformed_data = [{'Q': entry['question'], 'C': entry['code'], 'O':entry['output']} for entry in my_list]
    result_string = str(transformed_data).replace("'", "").replace('"', '').replace("{"," ").replace("}"," ")

    
    if csv_files:
        csvfile_message = "These are the following .csv files present in the resources/file/ directory. Read them using pd.read_csv() and perfomrn subsequent operations on it "
        csvfile_message += ", ".join(csv_files)

        payload = {
                "model" : "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": f"You are a helpful AI code generator. Only generate the python code.  IF A VARIABLE HAS BEEN DECLARED IN THE CHAT HISTORY BFORE, DONT DECLARE IT AGAIN!! If the question asks you to generate a plot, save the plot in the /app/resources/data directory. {csvfile_message}. Read them using pd.read_csv() and perform subsequent operations on them. QUESTION  - "+prompt+f" Chat history: {str(result_string)}"}],
                "temperature": 0.7
            }
    else:
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "You are a helpful AI code generator. Only generate the python code.  IF A VARIABLE HAS BEEN DECLARED IN THE CHAT HISTORY BFORE, DONT DECLARE IT AGAIN!!  If the question asks you to generate a plot, save the plot in the /app/resources/data directory. QUESTION  - "+prompt+f", Chat history: {str(result_string)}"}],
            "temperature": 0.7
        }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    code = response.json()
    code = code['choices'][0]['message']['content']
    pattern = r'```python(.*?)```'
    matches = re.findall(pattern, code, re.DOTALL)
    if not matches:
        return code, None  # Returning None as the second value
    extracted_code = '\n'.join(matches)
    lines = extracted_code.split('\n')[1:-1]
    modified_code = '\n'.join(lines)
    return response.json()['choices'][0]['message']['content'], modified_code




st.title("Code Generation and Running")

st.markdown(
    """
    <style>
        body {
            background-color: #f3f3f3;
            padding: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
        .title {
            color: #333;
            background-color: #ffd700;
            padding: 10px;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


if "messages" not in st.session_state:
    st.session_state.messages = []


files_list = [f for f in os.listdir("resources/file") if os.path.isfile(os.path.join("resources/file", f))]

files_to_delete = st.multiselect("Select files to delete", files_list)

for file_to_delete in files_to_delete:
    os.remove(os.path.join("files", file_to_delete))
    st.info(f"Deleted file: {file_to_delete}")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt=st.chat_input("Ask something!")
uploaded_file = st.file_uploader("Upload CSV", type=['csv'])


if prompt:

    if uploaded_file is not None:
        file_path = os.path.join("resources/file", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File uploaded successfully: {file_path}")


    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})
    question=prompt
    
    response, generated_code = generate_code(prompt)

    print("Response is: ", response)

    print("Question is: ", generated_code)
    
    with open('generated_code.py', 'w') as f:
        if generated_code==None:
            f.write(response)
        else:
            f.write(generated_code)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        assistant_response = response
        full_response = ""
        code_block = False

        for chunk in assistant_response.split("```"):
            if code_block:
                # Display code using st.code()
                st.code(chunk, language="python")
                code_block = False
            else:
                # Display non-code parts
                st.code(chunk, language="python")
                code_block = True

            time.sleep(0.05)


        with open("generated_code.py", "r") as f:
            code_to_execute = f.read()

        print("Sending code to container..."+code_to_execute)

        run_result = send_code_to_container(code_to_execute)

       
        print("Run result is: ", run_result)
        st.write(f"Output: {run_result['output']}")
        result=run_result

        if generated_code==None:
            update_chat_history(question, response, result['output'])
        else:
            update_chat_history(question, generated_code, result['output'])

        full_response += f"{result}"
        image_files = [file for file in os.listdir('resources/data/') if file.endswith(('.jpg', '.jpeg', '.png', '.gif'))]

        if image_files:
            for image_file in image_files:
                image_path = os.path.join('resources/data/', image_file)
                st.image(image_path)
                os.remove(image_path)

    st.session_state.messages.append({"role": "assistant", "content": full_response})





        

    

    

    




        

    

    

    


