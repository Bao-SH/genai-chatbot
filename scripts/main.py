import subprocess

def app_run():
    command = """
    cd app && \
    poetry run python main.py
    """
    subprocess.run(command, shell=True)