```python
def task_export_post_notebooks():
    """Export executed notebooks to HTML, PDF, and Markdown and clean temp PNGs"""
    for subdir in POSTS_DIR.iterdir():
        if not subdir.is_dir():
            continue

        notebook_name = subdir.name
        notebook_path = subdir / f"{notebook_name}.ipynb"
        html_output = subdir / f"{notebook_name}.html"
        pdf_output = subdir / f"{notebook_name}.pdf"
        md_output = subdir / f"{notebook_name}.md"
        
        if not notebook_path.exists():
            continue

        # Cells tagged "remove_input" contribute narrative prose that quotes computed
        # figures, so only their rendered output belongs in the post - not the source.
        remove_input = (
            "--TagRemovePreprocessor.enabled=True "
            "--TagRemovePreprocessor.remove_input_tags=remove_input"
        )

        yield {
            "name": notebook_name,
            "actions": [
                f"jupyter nbconvert --to=html --log-level=WARN {remove_input} --output={notebook_name} --output-dir={subdir} {notebook_path}",
                f"jupyter nbconvert --to=pdf --log-level=WARN {remove_input} --output={notebook_name} --output-dir={subdir} {notebook_path}",
                (clean_notebook_md_files, [subdir, notebook_name]),
                f"jupyter nbconvert --to=markdown --log-level=WARN {remove_input} --output={notebook_name} --output-dir={subdir} {notebook_path}",
                (clean_pdf_export_pngs, [subdir, notebook_name]),
            ],
            "file_dep": [notebook_path],
            "targets": [html_output, pdf_output, md_output],
            "verbosity": 2,
            "clean": [],  # Don't clean these files by default.
        }
```