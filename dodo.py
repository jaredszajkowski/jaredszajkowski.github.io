"""Run or update the project. This file uses the `doit` Python package. It works
like a Makefile, but is Python-based

"""

#######################################
## Import Libraries
#######################################

import sys

## Make sure the src folder is in the path
sys.path.insert(1, "./src/")

import shutil
import re
import yaml
from datetime import datetime
import subprocess
from os import environ, getcwd, path
from pathlib import Path
from colorama import Fore, Style, init

## Custom reporter: Print PyDoit Text in Green
# This is helpful because some tasks write to sterr and pollute the output in
# the console. I don't want to mute this output, because this can sometimes
# cause issues when, for example, LaTeX hangs on an error and requires
# presses on the keyboard before continuing. However, I want to be able
# to easily see the task lines printed by PyDoit. I want them to stand out
# from among all the other lines printed to the console.

from doit.reporter import ConsoleReporter
from settings import config

#######################################
## Configuration and Helpers for PyDoit
#######################################



try:
    in_slurm = environ["SLURM_JOB_ID"] is not None
except:
    in_slurm = False

class GreenReporter(ConsoleReporter):
    def write(self, stuff, **kwargs):
        doit_mark = stuff.split(" ")[0].ljust(2)
        task = " ".join(stuff.split(" ")[1:]).strip() + "\n"
        output = (
            Fore.GREEN
            + doit_mark
            + f" {path.basename(getcwd())}: "
            + task
            + Style.RESET_ALL
        )
        self.outstream.write(output)

if not in_slurm:
    DOIT_CONFIG = {
        "reporter": GreenReporter,
        # other config here...
        # "cleanforget": True, # Doit will forget about tasks that have been cleaned.
        "backend": "sqlite3",
        "dep_file": "./.doit-db.sqlite",
    }
else:
    DOIT_CONFIG = {
        "backend": "sqlite3", 
        "dep_file": "./.doit-db.sqlite"
    }
init(autoreset=True)

##################################
## Set directory variables
##################################

BASE_DIR = config("BASE_DIR")
CONTENT_DIR = config("CONTENT_DIR")
POSTS_DIR = config("POSTS_DIR")
PAGES_DIR = config("PAGES_DIR")
PUBLIC_DIR = config("PUBLIC_DIR")
SOURCE_DIR = config("SOURCE_DIR")



# DATA_DIR = config("DATA_DIR")
# MANUAL_DATA_DIR = config("MANUAL_DATA_DIR")
# OUTPUT_DIR = config("OUTPUT_DIR")
# OS_TYPE = config("OS_TYPE")
# PUBLISH_DIR = config("PUBLISH_DIR")
# USER = config("USER")
# PLOTS_DIR = config("PLOTS_DIR")
# TABLES_DIR = config("TABLES_DIR")

## Helpers for handling Jupyter Notebook tasks
# fmt: off
## Helper functions for automatic execution of Jupyter notebooks
environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"
def jupyter_execute_notebook(notebook):
    return f"jupyter nbconvert --execute --to notebook --ClearMetadataPreprocessor.enabled=True --log-level WARN --inplace ./src/{notebook}.ipynb"
# def jupyter_to_html(notebook, output_dir=OUTPUT_DIR):
def jupyter_to_html(notebook, output_dir):
    return f"jupyter nbconvert --to html --log-level WARN --output-dir='{output_dir}' ./src/{notebook}.ipynb"
# def jupyter_to_md(notebook, output_dir=OUTPUT_DIR):
def jupyter_to_md(notebook, output_dir):
    """Requires jupytext"""
    return f"jupytext --to markdown --log-level WARN --output-dir='{output_dir}' ./src/{notebook}.ipynb"
def jupyter_to_python(notebook, build_dir):
    """Convert a notebook to a python script"""
    return f"jupyter nbconvert --log-level WARN --to python ./src/{notebook}.ipynb --output _{notebook}.py --output-dir '{build_dir}'"
def jupyter_clear_output(notebook):
    return f"jupyter nbconvert --log-level WARN --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --inplace ./src/{notebook}.ipynb"
# fmt: on


def copy_file(origin_path, destination_path, mkdir=True):
    """Create a Python action for copying a file."""

    def _copy_file():
        origin = Path(origin_path)
        dest = Path(destination_path)
        if mkdir:
            dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origin, dest)

    return _copy_file


##################################
## Begin rest of PyDoit tasks here
##################################


def task_config():
    """Create empty directories for content, page, post, and public if they don't exist"""
    return {
        "actions": ["ipython ./src/settings.py"],
        "file_dep": ["./src/settings.py"],
        "targets": [CONTENT_DIR, PAGES_DIR, POSTS_DIR, PUBLIC_DIR],
        "verbosity": 2,
        "clean": [],  # Don't clean these files by default.
    }

def task_list_posts_subdirs():
    """Create a list of the subdirectories of the posts directory"""
    return {
        "actions": ["python ./src/list_posts_subdirs.py"],
        "file_dep": ["./src/settings.py"],
        # "targets": [POSTS_DIR],
        "verbosity": 2,
        "clean": [],  # Don't clean these files by default.
    }

def task_run_post_notebooks():
    """Execute notebooks that match their subdirectory names"""
    for subdir in POSTS_DIR.iterdir():
        if subdir.is_dir():
            notebook_path = subdir / f"{subdir.name}.ipynb"

            if notebook_path.exists():
                yield {
                    "name": subdir.name,
                    "actions": [f"jupyter nbconvert --execute --to notebook --inplace --log-level=ERROR {notebook_path}"],
                    "file_dep": [notebook_path],
                    # "targets": [notebook_path],  # optional if you want doit to track it
                    "verbosity": 2,
                }

def task_export_post_notebooks():
    """Export executed notebooks to HTML and PDF"""
    for subdir in POSTS_DIR.iterdir():
        if subdir.is_dir():
            notebook_path = subdir / f"{subdir.name}.ipynb"
            html_output = subdir / f"{subdir.name}.html"
            pdf_output = subdir / f"{subdir.name}.pdf"

            if notebook_path.exists():
                yield {
                    "name": subdir.name,
                    "actions": [
                        f"jupyter nbconvert --to=html --log-level=WARN --output={html_output} {notebook_path}",
                        f"jupyter nbconvert --to=pdf --log-level=WARN --output={pdf_output} {notebook_path}"
                    ],
                    "file_dep": [notebook_path],
                    "targets": [html_output, pdf_output],
                    "verbosity": 2,
                    "clean": [],  # Don't clean these files by default.
                }

def task_build_post_indexes():
    """Run build_index.py in each post subdirectory to generate index.md"""
    script_path = SOURCE_DIR / "build_index.py"

    for subdir in POSTS_DIR.iterdir():
        if subdir.is_dir() and (subdir / "index_temp.md").exists():
            def run_script(subdir=subdir):
                subprocess.run(
                    ["python", str(script_path)],
                    cwd=subdir,
                    check=True
                )

            yield {
                "name": subdir.name,
                "actions": [run_script],
                "file_dep": [
                    subdir / "index_temp.md",
                    subdir / "index_dep.txt",
                    script_path,
                ],
                "targets": [subdir / "index.md"],
                "verbosity": 2,
                "clean": [],  # Don't clean these files by default.
            }

def task_build_site():
    """Build the Hugo static site"""
    return {
        "actions": ["hugo"],
        "verbosity": 2,
        "clean": [],  # Don't clean these files by default.
    }

# def task_push_repo():
#     """Push the full repo to GitHub after site build"""
#     return {
#         "actions": [
#             "git add .",
#             'git commit -am "🚀 Rebuild site"',
#             "git push"
#         ],
#         "task_dep": ["build_site"],
#         "verbosity": 2,
#         "clean": False
#     }

# Helper function to extract front matter
def extract_front_matter(index_path):
    """Extract front matter as a dict from a Hugo index.md file"""
    text = index_path.read_text()
    match = re.search(r"(?s)^---(.*?)---", text)
    if match:
        return yaml.safe_load(match.group(1))
    return {}

def task_copy_notebook_exports():
    """Copy notebook HTML exports into the correct Hugo public/ date-based folders"""
    for subdir in POSTS_DIR.iterdir():
        if subdir.is_dir():
            html_file = subdir / f"{subdir.name}.html"
            index_md = subdir / "index.md"

            if not html_file.exists() or not index_md.exists():
                continue

            # Extract slug and date from front matter
            front_matter = extract_front_matter(index_md)
            slug = front_matter.get("slug", subdir.name)
            date_str = front_matter.get("date")
            if not date_str:
                continue

            # Format path like: public/YYYY/MM/DD/slug/
            date_obj = datetime.fromisoformat(date_str)
            public_path = PUBLIC_DIR / f"{date_obj:%Y/%m/%d}" / slug
            target_path = public_path / f"{slug}.html"

            def copy_html(src=html_file, dest=target_path):
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                print(f"✅ Copied {src} → {dest}")

            yield {
                "name": subdir.name,
                "actions": [copy_html],
                "file_dep": [html_file, index_md],
                "targets": [target_path],
                "task_dep": ["build_site"],
                "verbosity": 2,
            }

def task_deploy_site():
    """Prompt for a commit message and push to GitHub"""
    def commit_and_push():
        message = input("What is the commit message? ")
        if not message.strip():
            print("❌ Commit message cannot be empty.")
            return 1  # signal failure
        import subprocess
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-am", message], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Pushed to GitHub.")

    return {
        "actions": [commit_and_push],
        "task_dep": ["build_site"],
        "verbosity": 2,
        "clean": [],  # Don't clean these files by default.
    }


def task_build_all():
    return {
        "actions": None,
        "task_dep": [
            "run_post_notebooks",
            "export_post_notebooks",
            "build_post_indexes",
            "build_site",
            "copy_notebook_exports",
            "deploy_site",
        ]
    }





##################################
## Pull Data
##################################

# # This is needed for F-F BE/ME portfolios
# def task_pull_ken_french_data():
#     """Pull Data from Ken French's Website """

#     return {
#         "actions": [
#             "ipython src/settings.py",
#             "ipython src/pull_ken_french_data.py",
#         ],
#         "targets": [
#             Path(DATA_DIR) / "6_Portfolios_2x3.xlsx",
#             Path(DATA_DIR) / "25_Portfolios_5x5.xlsx",
#             Path(DATA_DIR) / "100_Portfolios_10x10.xlsx",
#         ],
#         "file_dep": ["./src/settings.py", "./src/pull_ken_french_data.py"],
#         "clean": [],  # Don't clean these files by default.
#         "verbosity": 2,
#     }

# # This is needed for CRSP value weighted index
# def task_pull_CRSP_index():
#     """ Pull CRSP Value-Weighted Index """
#     file_dep = [
#         "./src/pull_CRSP_index.py",
#         ]
#     file_output = [
#         "crsp_value_weighted_index.csv",
#         ]
#     targets = [DATA_DIR / file for file in file_output]

#     return {
#         "actions": [
#             "ipython ./src/pull_CRSP_index.py",
#         ],
#         "targets": targets,
#         "file_dep": file_dep,
#         "clean": [],  # Don't clean these files by default.
#     }

##############################$
## Notebook Tasks
##############################$

# notebook_tasks = {
#     "01_Market_Expectations_In_The_Cross-Section_Of_Present_Values_Final.ipynb": {
#         "file_dep": [],
#         "targets": [],
#     },
#     "run_regressions.ipynb": {
#         "file_dep": [],
#         "targets": [],
#     },
# }

# def task_convert_notebooks_to_scripts():
#     """Convert notebooks to script form to detect changes to source code rather
#     than to the notebook's metadata.
#     """
#     build_dir = Path(OUTPUT_DIR)

#     for notebook in notebook_tasks.keys():
#         notebook_name = notebook.split(".")[0]
#         yield {
#             "name": notebook,
#             "actions": [
#                 jupyter_clear_output(notebook_name),
#                 jupyter_to_python(notebook_name, build_dir),
#             ],
#             "file_dep": [Path("./src") / notebook],
#             "targets": [OUTPUT_DIR / f"_{notebook_name}.py"],
#             "clean": True,
#             "verbosity": 0,
#         }

# # fmt: off
# def task_run_notebooks():
#     """Preps the notebooks for presentation format.
#     Execute notebooks if the script version of it has been changed.
#     """
#     for notebook in notebook_tasks.keys():
#         notebook_name = notebook.split(".")[0]
#         yield {
#             "name": notebook,
#             "actions": [
#                 """python -c "import sys; from datetime import datetime; print(f'Start """ + notebook + """: {datetime.now()}', file=sys.stderr)" """,
#                 jupyter_execute_notebook(notebook_name),
#                 jupyter_to_html(notebook_name),
#                 copy_file(
#                     Path("./src") / f"{notebook_name}.ipynb",
#                     OUTPUT_DIR / f"{notebook_name}.ipynb",
#                     mkdir=True,
#                 ),
#                 jupyter_clear_output(notebook_name),
#                 # jupyter_to_python(notebook_name, build_dir),
#                 """python -c "import sys; from datetime import datetime; print(f'End """ + notebook + """: {datetime.now()}', file=sys.stderr)" """,
#             ],
#             "file_dep": [
#                 OUTPUT_DIR / f"_{notebook_name}.py",
#                 *notebook_tasks[notebook]["file_dep"],
#             ],
#             "targets": [
#                 OUTPUT_DIR / f"{notebook_name}.html",
#                 OUTPUT_DIR / f"{notebook_name}.ipynb",
#                 *notebook_tasks[notebook]["targets"],
#             ],
#             "clean": True,
#         }
# # fmt: on

# ###############################################################
# ## Task below is for LaTeX compilation
# ###############################################################

# def task_compile_latex_docs():
#     """Compile the LaTeX documents to PDFs"""
#     file_dep = [
#         "./reports/project.tex",
#     ]
#     targets = [
#         "./reports/project.pdf",
#     ]

#     return {
#         "actions": [
#             "latexmk -xelatex -halt-on-error -cd ./reports/project.tex",  # Compile
#             "latexmk -xelatex -halt-on-error -c -cd ./reports/project.tex",  # Clean
#         ],
#         "targets": targets,
#         "file_dep": file_dep,
#         "clean": True,
#     }