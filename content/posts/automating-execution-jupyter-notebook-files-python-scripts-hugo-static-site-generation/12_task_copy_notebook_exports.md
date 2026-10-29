```python
def task_copy_notebook_exports():
    """Copy notebook HTML exports into the Hugo static/posts/<slug>/ folders"""
    for subdir in POSTS_DIR.iterdir():
        if subdir.is_dir():
            notebook_file = subdir / f"{subdir.name}.ipynb"
            html_file = subdir / f"{subdir.name}.html"
            index_md = subdir / "index.md"

            # Gate on the notebook rather than on the export and index.md: for a
            # brand-new post those two are produced earlier in this same run, so
            # testing them here - while the task list is still being built - would
            # silently skip the post.
            if not notebook_file.exists():
                continue

            def copy_html(src=html_file, index=index_md, name=subdir.name):
                # Extract slug and date from front matter
                front_matter = extract_front_matter(index)
                slug = front_matter.get("slug", name)
                date_str = front_matter.get("date")
                if not date_str:
                    print(f"⏩ Skipped {src.name}: no date in front matter")
                    return

                # Old functionality to format path based on date
                # # Format path like: public/YYYY/MM/DD/slug/
                # date_obj = datetime.fromisoformat(date_str)
                # public_path = PUBLIC_DIR / f"{date_obj:%Y/%m/%d}" / slug
                # target_path = public_path / f"{slug}.html"

                # New functionality to ignore date and just use slug
                # Format path like: static/posts/slug/
                dest = STATIC_DIR / "posts" / slug / f"{slug}.html"
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                print(f"✅ Copied {src} → {dest}")

            yield {
                "name": subdir.name,
                "actions": [copy_html],
                # No "targets": the slug, and so the destination path, is only
                # known once index.md has been generated - which happens after
                # this task list is built. file_dep alone drives the up-to-date
                # check, and the copy itself is cheap and idempotent.
                "file_dep": [html_file, index_md],
                "task_dep": ["build_post_indices"],
                "verbosity": 2,
                "clean": [],  # Don't clean these files by default.
            }
```