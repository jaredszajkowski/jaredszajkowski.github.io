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
project_root = script_directory.parents[2]  # Adjust if necessary
static_directory = project_root / "static"
public_directory = project_root / "public"

print("Script Directory:", script_directory)
print("Project Root:", project_root)
print("Static Directory:", static_directory)
print("Public Directory:", public_directory)

# Function to convert Jupyter notebook to various formats
def convert_notebook(notebook: str, to_format: str):
    notebook_path = script_directory / f"{notebook}.ipynb"
    output_path = script_directory / f"{notebook}.{to_format}"

    cmd = [
        "jupyter", "nbconvert",
        f"--to={to_format}",
        "--log-level=WARN",
        f"--output={output_path.name}",
        str(notebook_path)
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Converted {notebook}.ipynb to {to_format}.")

        # Copy HTML to public/.../{notebook}/
        if to_format == "html":
            public_target_dir = public_directory / "2025" / "03" / "01" / notebook

            destination = public_target_dir / output_path.name
            shutil.copy2(output_path, destination)
            print(f"📁 Copied {output_path.name} to {destination}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error converting {notebook}.ipynb to {to_format}: {e}")

# Run conversions
convert_notebook(notebook, "html")
convert_notebook(notebook, "pdf")
