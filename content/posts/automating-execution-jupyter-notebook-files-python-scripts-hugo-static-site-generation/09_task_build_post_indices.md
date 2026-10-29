```python
def task_build_post_indices():
    for subdir in POSTS_DIR.iterdir():
        """Run build_index.py in each post subdirectory to generate index.md."""
        if subdir.is_dir() and (subdir / "index_temp.md").exists():

            script_path = SOURCE_DIR / "build_index.py"

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

        """Combine the Jupyter notebook Markdown export with the frontmatter.md file in each post subdirectory to generate index.md."""
        if subdir.is_dir() and (subdir / "frontmatter.md").exists():
            frontmatter_path = subdir / "frontmatter.md"
            nb_md_path = subdir / f"{subdir.name}.md"
            index_path = subdir / "index.md"

            def build_index(frontmatter=frontmatter_path, nb_md=nb_md_path, index=index_path):
                content = frontmatter.read_text().rstrip() + "\n\n" + nb_md.read_text().lstrip()
                content = content.rstrip() + "\n\n## Code\n\n{{< post-files >}}\n"
                index.write_text(content)

            yield {
                "name": subdir.name,
                "actions": [build_index],
                "file_dep": [frontmatter_path, nb_md_path],
                "targets": [index_path],
                "task_dep": [f"export_post_notebooks:{subdir.name}"],
                "verbosity": 2,
                "clean": [],  # Don't clean these files by default.
            }
```