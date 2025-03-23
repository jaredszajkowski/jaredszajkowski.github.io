# convert_notebook.py

import subprocess
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description="Convert a Jupyter notebook to HTML and PDF.")
parser.add_argument("notebook_path", help="Full path to the notebook file")
args = parser.parse_args()

notebook_path = Path(args.notebook_path)
notebook_stem = notebook_path.stem
output_dir = notebook_path.parent

def convert_notebook(notebook: Path, to_format: str):
    output_filename = f"{notebook_stem}.{to_format}"
    cmd = [
        "jupyter", "nbconvert",
        f"--to={to_format}",
        "--log-level=WARN",
        f"--output={output_filename}",
        f"--output-dir={output_dir}",
        str(notebook)
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Converted {notebook.name} to {to_format}.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error converting {notebook.name} to {to_format}: {e}")

convert_notebook(notebook_path, "html")
convert_notebook(notebook_path, "pdf")

