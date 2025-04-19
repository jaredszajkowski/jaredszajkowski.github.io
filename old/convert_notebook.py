# Simple functions to convert a juptyer notebook to a various formats
import subprocess
import shutil
from pathlib import Path
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Convert a Jupyter notebook to HTML and PDF.")
parser.add_argument("notebook", help="Name of the notebook (without .ipynb extension)")
args = parser.parse_args()

notebook = args.notebook

# Paths
script_directory = Path(__file__).parent
print("Script Directory:", script_directory)

# Function to convert Jupyter notebook to various formats
def convert_notebook(notebook: str, to_format: str):
    output_file = script_directory / f"{notebook}.{to_format}"
    cmd = [
        "jupyter", "nbconvert",
        f"--to={to_format}",
        "--log-level=WARN",
        f"--output={output_file}",
        f"{script_directory}/{notebook}.ipynb"
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Converted {notebook}.ipynb to {to_format}.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error converting {notebook}.ipynb to {to_format}: {e}")

# Run conversions
convert_notebook(notebook, "html")
convert_notebook(notebook, "pdf")