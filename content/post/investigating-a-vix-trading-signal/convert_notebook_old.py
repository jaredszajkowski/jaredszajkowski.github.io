# Simple functions to convert a juptyer notebook to a various formats

import subprocess
from pathlib import Path

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
        print(f"Successfully converted {notebook}.ipynb to {to_format}.")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {notebook}.ipynb to {to_format}: {e}")

# Convert the notebook to HTML and PDF
convert_notebook("investigating-a-vix-trading-signal", "html")
convert_notebook("investigating-a-vix-trading-signal", "pdf")