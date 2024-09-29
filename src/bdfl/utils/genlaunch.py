import json
import os

from loguru import logger


def _filenames_to_launch(filenames: list):
    launch_options = []
    for filepath in filenames:
        launch_options.append(
            {
                "name": filepath,
                "type": "python",
                "request": "launch",
                "program": filepath,
                "console": "integratedTerminal",
                "justMyCode": True,
            }
        )
    return launch_options


def _find_main_files(directory: str):
    main_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    content = f.read()
                    if 'if __name__ == "__main__":' in content:
                        main_files.append(filepath)
    return main_files


def _add_current_file(launch_options: list) -> list:
    launch_options.append(
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": True,
        }
    )
    return launch_options


def genlaunch(dirs: list) -> dict:
    """
    Update the launch.json with your executable scripts and configs
    """
    _find_main_files("spotify_playlists")
    output_directory = r".vscode"
    filenames = []
    for directory in dirs:
        filenames += _find_main_files(directory)
    launch_options = _filenames_to_launch(filenames)
    launch_options = _add_current_file(launch_options)
    launch_json = {"version": "0.2.0", "configurations": launch_options}
    os.makedirs(output_directory, exist_ok=True)
    with open(os.path.join(output_directory, "launch.json"), "w") as outfile:
        json.dump(launch_json, outfile, indent=2)
    logger.info("Updated launch.json")
    return launch_json
