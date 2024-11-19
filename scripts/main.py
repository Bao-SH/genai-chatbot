import subprocess
import uvicorn

def app_run():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload
    )

# runs tests
def app_test():
    command = """
    cd app && \
    poetry run pytest -m 'not integration'
    """
    subprocess.run(command, shell=True)