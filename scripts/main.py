import subprocess

def app_run():
    command = """
    cd app && \
    poetry run python main.py
    """
    subprocess.run(command, shell=True)

# runs tests
def app_test():
    command = """
    cd app && \
    poetry run pytest -m 'not integration'
    """
    subprocess.run(command, shell=True)