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

def generate_code(prompt):        
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': ''
    }
    csv_files = [file for file in os.listdir('resources/file') if file.endswith('.csv')]
    if csv_files:
        csvfile_message = "These are the following .csv files present in the resources/file/ directory. Read them using pd.read_csv() and perfomrn subsequent operations on it "
        csvfile_message += ", ".join(csv_files)

        payload = {
                "model" : "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": f"You are a helpful AI code generator. Only generate the python code.  If the question asks you to generate a plot, save the plot in the /app/resources/data directory. {csvfile_message}. Read them using pd.read_csv() and perform subsequent operations on them. QUESTION  - "+prompt}],
                "temperature": 0.7
            }
    else:
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "You are a helpful AI code generator. Only generate the python code. If the question asks you to generate a plot, save the plot in the /app/resources/data directory. QUESTION  - "+prompt}],
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
    

        build_result = subprocess.run(["docker", "build", "-t", "code_runner", "."], capture_output=True, text=True)
        print(build_result.stdout)
        print(build_result.stderr)

        subprocess.run(["docker", "rm", "-f", "code_runner_instance"], capture_output=True, text=True)

        run_result = subprocess.run(["docker", "run", "--name", "code_runner_instance", "-v", "/Users/abhinandganesh/desktop/code_runner/resources:/app/resources", "code_runner", "python", "/app/execute_code.py"], capture_output=True, text=True)

        if run_result.stderr:
            print(run_result.stderr)
        else:
            print("Run result is: ", run_result.stdout)
            result = json.loads(run_result.stdout)
            st.write(f"Output: {result['output']}")
            print(result)

        full_response += f"{result}"
        image_files = [file for file in os.listdir('resources/data/') if file.endswith(('.jpg', '.jpeg', '.png', '.gif'))]

        if image_files:
            for image_file in image_files:
                image_path = os.path.join('resources/data/', image_file)
                st.image(image_path)
                os.remove(image_path)

    st.session_state.messages.append({"role": "assistant", "content": full_response})





        

    

    

    




        

    

    

    


