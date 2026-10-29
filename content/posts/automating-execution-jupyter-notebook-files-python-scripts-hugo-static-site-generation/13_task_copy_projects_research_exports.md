```python
def task_copy_projects_research_exports():
    """Copy all HTML files from the projects-research page to the Hugo static/ folder"""
    src_dir = PAGES_DIR / "projects-research"
    dest_dir = STATIC_DIR / "projects-research"

    html_files = list(src_dir.glob("*.html"))
    if not html_files:
        return  # Skip if no HTML files found

    def copy_all_html():
        dest_dir.mkdir(parents=True, exist_ok=True)
        for html_file in html_files:
            dest_path = dest_dir / html_file.name
            shutil.copy2(html_file, dest_path)
            print(f"✅ Copied {html_file} → {dest_path}")

    return {
        "actions": [copy_all_html],
        "file_dep": html_files,
        "targets": [dest_dir / f.name for f in html_files],
        "task_dep": ["copy_notebook_exports"],
        "verbosity": 2,
        "clean": [],  # Don't clean these files by default.
    }
```