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
        "task_dep": ["create_schwab_callback"],
        "verbosity": 2,
        "clean": [],  # Don't clean these files by default.
    }
```