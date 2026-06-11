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


@invoke.task
def ui(c, port=8501):
    """
    Start the Streamlit UI application
    
    Args:
        port: Port for the Streamlit server (default: 8501)
    """
    _run(c, f"poetry run streamlit run src/bdfl/ui/app.py --server.port {port}")


@invoke.task
def docs(c, serve=False, port=8000):
    """
    Build Sphinx documentation from Markdown files
    
    Args:
        serve: Start a local web server to view docs
        port: Port for the web server (default: 8000)
    """
    # Build the documentation
    _run(c, "poetry run sphinx-build -b html docs docs/_build/html")
    
    if serve:
        import webbrowser
        import threading
        import time
        from http.server import HTTPServer, SimpleHTTPRequestHandler
        import os
        
        # Change to the build directory
        build_dir = "docs/_build/html"
        os.chdir(build_dir)
        
        # Start the server in a separate thread
        def start_server():
            server = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
            print(f"\n📚 Documentation server running at http://localhost:{port}")
            print("Press Ctrl+C to stop the server\n")
            server.serve_forever()
        
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # Wait a moment then open browser
        time.sleep(1)
        webbrowser.open(f"http://localhost:{port}")
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Documentation server stopped")
