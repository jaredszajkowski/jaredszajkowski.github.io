---
title: Automating Execution of Jupyter Notebook Files, Python Scripts, and Hugo Static Site Generation
description: A full-stack approach using doit.
slug: automating-execution-jupyter-notebook-files-python-scripts-hugo-static-site-generation
date: 2025-06-29 00:00:01+0000
# lastmod: 2025-05-07 00:00:01+0000
image: cover.jpg
draft: false
categories:
    - Tech
    - Python
    - Hugo
# tags:
#     - Python
#     - Hugo
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

## Introduction

In this post, I'll cover the implementation of [doit](https://pydoit.org/) to automate the execution of Jupyter notebook files, Python scripts, and building the Hugo static site. Many of the concepts covered below were introduced recently in [FINM 32900 - Full-Stack Quantitative Finance](https://finmath.uchicago.edu/curriculum/degree-concentrations/financial-computing/finm-32900/). This course emphasized the "full stack" approach, including the following:

* Use of GitHub
* Virtual environments
* Environment variables
* Use of various data sources (particularly WRDS)
* Processing/cleaning data
* GitHub actions
* Publishing data
* Restricting access to GitHub hosted sites

## Motivation

The primary motivation for automation came from several realizations:

1. Setting directory variables would avoid any issues with managing where the static files were stored locally
2. I wanted to be able to pull updated data, execute Jupyter notebooks, and update the posts within my Hugo site without a manual intervention and processes
3. I like to include the html and PDF exports of the Jupyter notebooks, which required copying the exports to the "Public" folder of the website
4. I needed a system to build the "index.md" files that are present in each post directory, and automatically include Python code and functions (again, without copying/pasting or manual processes)

## dodo.py

The `dodo.py` file in the primary directory is referenced by `doit` and includes all imports, functions, environment variables, etc. as required to execute the desired code. My `dodo.py` is broken down as follows:

### Imports

The inital imports are as follows:

<!-- INSERT_01_Imports_HERE -->

This first adds the `/src/` subdirectory to the path (required later on), and then imports any other required modules. I prefer to sort all imports alphabetically for easy reference and readability.

### Print PyDoit Text in Green

Next, I use the following code to help differentiate the various outputs in the termial when executing `doit`:

<!-- INSERT_02_Print_Green_HERE -->

### Set Directory Variables

Next, I establish the variables that reference some of the more important directories and subdirectories in the project:

<!-- INSERT_03_Directory_Variables_HERE -->

These directory variables are set from the `settings.py` file in the `/src/` directory. Setting these directory variables allows me to reference them at any point later on in the `dodo.py` file.

### Helper Functions

The following are several helper functions that are referenced in the tasks. These are somewhat self explanatory, and are used by the task functions in the next section below:

```python
#######################################
## Helper functions
#######################################

def copy_file(origin_path, destination_path, mkdir=True):
    """Create a Python action for copying a file."""

    def _copy_file():
        origin = Path(origin_path)
        dest = Path(destination_path)
        if mkdir:
            dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origin, dest)

    return _copy_file

def extract_front_matter(index_path):
    """Extract front matter as a dict from a Hugo index.md file."""
    text = index_path.read_text()
    match = re.search(r"(?s)^---(.*?)---", text)
    if match:
        return yaml.safe_load(match.group(1))
    return {}

def notebook_source_hash(notebook_path):
    """Compute a SHA-256 hash of the notebook's code and markdown cells. This includes all whitespace and comments."""
    import nbformat
    import hashlib

    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    relevant_cells = [
        cell["source"]
        for cell in nb.cells
        if cell.cell_type in {"code", "markdown"}
    ]
    full_content = "\n".join(relevant_cells)
    return hashlib.sha256(full_content.encode("utf-8")).hexdigest()

def clean_pdf_export_pngs(subdir, notebook_name):
    """Remove .png files created by nbconvert during PDF export."""
    pattern = f"{notebook_name}_*_*.png"
    deleted = False
    for file in subdir.glob(pattern):
        print(f"🧹 Removing nbconvert temp image: {file}")
        file.unlink()
        deleted = True
    if not deleted:
        print(f"✅ No temp PNGs to remove for {notebook_name}")
```

### Tasks

Next, we will look at the individual tasks that are being executed by `doit`.

The config task creates the base directories for the Hugo site:

```python
#######################################
## PyDoit tasks
#######################################

def task_config():
    """Create empty directories for content, page, post, and public if they don't exist"""
    return {
        "actions": ["ipython ./src/settings.py"],
        "file_dep": ["./src/settings.py"],
        "targets": [CONTENT_DIR, PAGES_DIR, POSTS_DIR, PUBLIC_DIR],
        "verbosity": 2,
        "clean": [],  # Don't clean these files by default.
    }
```

The `task_list_posts_subdirs` function is not really necessary, but was used as an initial starting point for when I began building the `dodo.py` file:

```python
def task_list_posts_subdirs():
    """Create a list of the subdirectories of the posts directory"""
    return {
        "actions": ["python ./src/list_posts_subdirs.py"],
        "file_dep": ["./src/settings.py"],
        # "targets": [POSTS_DIR],
        "verbosity": 2,
        "clean": [],  # Don't clean these files by default.
    }
```

The `task_run_post_notebooks` function performs the following actions:

1. Finds all of the "post" subdirectories
2. In each "post" directory, it executes the jupyter notebook file (if found) that has the same name as the post
3. The hash of the non-markdown cells in the notebook is also checked, and if the hash has not changed since the last run, then it skips executing the notebook
4. After the notebook is executed (or not), the log is updated with the date and action

```python
def task_run_post_notebooks():
    """Execute notebooks that match their subdirectory names and only when code or markdown content has changed"""
    for subdir in POSTS_DIR.iterdir():
        if not subdir.is_dir():
            continue

        notebook_path = subdir / f"{subdir.name}.ipynb"
        if not notebook_path.exists():
            continue  # ✅ Skip subdirs with no matching notebook

        hash_file = subdir / f"{subdir.name}.last_source_hash"
        log_file = subdir / f"{subdir.name}.log"
        
        def source_has_changed(path=notebook_path, hash_path=hash_file, log_path=log_file):
            current_hash = notebook_source_hash(path)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if hash_path.exists():
                old_hash = hash_path.read_text().strip()
                if current_hash != old_hash:
                    print(f"🔁 Change detected in {path.name}")
                    return False  # needs re-run

                # ✅ No change → log as skipped
                with log_path.open("a") as log:
                    log.write(f"[{timestamp}] ⏩ Skipped (no changes): {path.name}\n")
                print(f"⏩ No change in hash for {path.name}")
                return True

            # 🆕 No previous hash → must run
            print(f"🆕 No previous hash found for {path.name}")
            return False
        
        def run_and_log(path=notebook_path, hash_path=hash_file, log_path=log_file):
            start_time = time.time()
            subprocess.run([
                "jupyter", "nbconvert",
                "--execute",
                "--to", "notebook",
                "--inplace",
                "--log-level=ERROR",
                str(path)
            ], check=True)
            elapsed = round(time.time() - start_time, 2)

            new_hash = notebook_source_hash(path)
            hash_path.write_text(new_hash)
            print(f"✅ Saved new hash for {path.name}")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f"[{timestamp}] ✅ Executed {path.name} in {elapsed}s\n"
            with log_path.open("a") as f:
                f.write(log_msg)

            print(log_msg.strip())

        yield {
            "name": subdir.name,
            "actions": [run_and_log],
            "file_dep": [notebook_path],
            "uptodate": [source_has_changed],
            "verbosity": 2,
        }
```

Next, the `task_export_post_notebooks` function exports the executed jupyter notebook to both HTML and PDF formats.

```python
def task_export_post_notebooks():
    """Export executed notebooks to HTML and PDF, and clean temp PNGs"""
    for subdir in POSTS_DIR.iterdir():
        if not subdir.is_dir():
            continue

        notebook_name = subdir.name
        notebook_path = subdir / f"{notebook_name}.ipynb"
        html_output = subdir / f"{notebook_name}.html"
        pdf_output = subdir / f"{notebook_name}.pdf"

        if not notebook_path.exists():
            continue

        yield {
            "name": notebook_name,
            "actions": [
                f"jupyter nbconvert --to=html --log-level=WARN --output={html_output} {notebook_path}",
                f"jupyter nbconvert --to=pdf --log-level=WARN --output={pdf_output} {notebook_path}",
                (clean_pdf_export_pngs, [subdir, notebook_name])
            ],
            "file_dep": [notebook_path],
            "targets": [html_output, pdf_output],
            "verbosity": 2,
            "clean": [],  # Don't clean these files by default.
        }
```

The `task_build_post_indices` builds each `index.md` file within each "post" directory. It looks for an `index_temp.md` and an `index_dep.txt` file, which contains the dependencies required to build the `index.md` file. The dependencies are established within the jupyter notebook for each post, and the `index_dep.txt` file is also updated when the notebook is executed.

```python
def task_build_post_indices():
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
```

Here's an example of when the `index_dep.txt` file is generated, and then updated with a markdown file dependency is generated with the [`export_track_md_deps`](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#export_track_md_deps) function:

```python
# Create file to track markdown dependencies
dep_file = Path("index_dep.txt")
dep_file.write_text("")

# Copy this <!-- INSERT_01_VIX_Stats_By_Year_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="01_VIX_Stats_By_Year.md", content=vix_stats_by_year.to_markdown(floatfmt=".2f"))

# Copy this <!-- INSERT_02_VVIX_DF_Info_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="02_VVIX_DF_Info.md", content=df_info_markdown(vix))

# Copy this <!-- INSERT_11_Net_Profit_Percent_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="11_Net_Profit_Percent.md", content=net_profit_percent_str)
```

Moving on, the `task_clean_public` removes the public directory within the static site. This is necessary to clean out any erroneous files or directories that are changed when the site is rebuilt.

```python
def task_clean_public():
    """Remove the Hugo public directory before rebuilding the site."""
    def remove_public():
        if PUBLIC_DIR.exists():
            shutil.rmtree(PUBLIC_DIR)
            print(f"🧹 Deleted {PUBLIC_DIR}")
        else:
            print(f"ℹ️  {PUBLIC_DIR} does not exist, nothing to delete.")
    return {
        "actions": [remove_public],
        "verbosity": 2,
        "clean": [],  # Don't clean these files by default.
    }
```

The `task_build_site` builds the Hugo static site.

```python
def task_build_site():
    """Build the Hugo static site"""
    return {
        "actions": ["hugo"],
        "task_dep": ["clean_public"],
        "verbosity": 2,
        "clean": [],  # Don't clean these files by default.
    }
```

The `task_copy_notebook_exports` copies the HTML and PDF exports generated above to the public folder. This is necessary due to how Hugo handles HTML and PDF files and excludes those when generating the static site public directories and files.

```python
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
                "clean": [],  # Don't clean these files by default.
            }
```

The `task_create_schwab_callback` creates a simple HTML file that will read the authorization code when using oauth with the Schwab API.

```python
def task_create_schwab_callback():
    """Create a Schwab callback URL by creating /public/schwab_callback/index.html and placing the html code in it"""
    def create_callback():
        callback_path = PUBLIC_DIR / "schwab_callback" / "index.html"
        callback_path.parent.mkdir(parents=True, exist_ok=True)
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Schwab OAuth Code</title>
    <script>
        const params = new URLSearchParams(window.location.search);
        const code = params.get("code");
        document.write("<h1>Authorization Code:</h1><p>" + code + "</p>");
    </script>
</head>
<body></body>
</html>"""
        with open(callback_path, "w") as f:
            f.write(html)
        print(f"✅ Created Schwab callback page at {callback_path}")

    return {
        "actions": [create_callback],
        "task_dep": ["copy_notebook_exports", "clean_public"],
        "verbosity": 2,
        "clean": [],  # Don't clean these files by default.
    }
```

Finally, the `task_deploy_site` adds any new files, commits the changes, prompts for a message, and pushes the updates to GitHub.

```python
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
        "task_dep": ["create_schwab_callback"],
        "verbosity": 2,
        "clean": [],  # Don't clean these files by default.
    }
```

As (likely) expected, a good portion of the above code was generated by ChatGPT - somewhere ~ 50%-75%. The balance was generated by myself or modified using the base code provided. Importantly, the general idea of automating the entire process within Hugo and processing the post subdirectories is original (as far as I know).

Finally, the complete `dodo.py` and `settings.py` files are available in the jupyter notebook / HTML / PDF exports linked below.

## Executing doit

To execute `doit`, simply run:

    $ doit

in the terminal after changing to the high level directory.

Alternatively, you can list the individual tasks with:

    $ doit list

and then execute individually, such as:

    $ doit build_post_indices

And finally, `doit` can be forced to execute all tasks with:

    $ doit --always

or an individual task with:

    $ doit --always build_post_indices

## References

1. https://pydoit.org/
2. https://github.com/jmbejara

## Code

The jupyter notebook with the functions and all other code is available [here](automating-execution-jupyter-notebook-files-python-scripts-hugo-static-site-generation.ipynb).</br>
The html export of the jupyter notebook is available [here](automating-execution-jupyter-notebook-files-python-scripts-hugo-static-site-generation.html).</br>
The pdf export of the jupyter notebook is available [here](automating-execution-jupyter-notebook-files-python-scripts-hugo-static-site-generation.pdf).