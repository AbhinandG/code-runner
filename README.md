# Key commands

To build the docker container, execute 

```
docker build -t code_runner .
```

To run it, execute

```
docker run -d -p 12345:12345 -p 5555:5555 -v /your_path_to_the_repository/code_runner/resources:/app/resources code_runner
```

To run the streamlit UI, execute

```
streamlit run main.py
```
