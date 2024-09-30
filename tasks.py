import invoke
from bdfl.utils import genlaunch

DIRS = ["src", "tests"]

def _run(c, command):
    print(">>", command)
    c.run(command)

@invoke.task
def launch(c, dirs: list = []):
    """
    Regenerates the launch.json debugger config in vscode
    """
    if dirs == []:
        dirs = DIRS
    genlaunch(DIRS)

@invoke.task
def format(c, dirs: list = []):
    """
    Run code autoformatting with black, isort, and flake8
    """
    if dirs == []:
        dirs = DIRS
    for dir in dirs:
        _run(c, f"ruff format {dir}")
        _run(c, f"ruff check {dir} --fix")


@invoke.task(format)
def docs(c):
    """
    Update the documentation directory and update gh-pages from master
    """
    _run(c, "pdoc src/spotify_playlists -o docs")
