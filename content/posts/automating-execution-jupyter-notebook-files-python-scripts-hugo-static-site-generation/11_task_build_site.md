```python
def task_build_site():
    """Build the Hugo static site.

    Runs last: `hugo` copies static/ into public/, so every task that writes
    into static/ has to have finished before this point or its output misses
    the build and only lands in public/ on the following run.
    """
    return {
        "actions": ["hugo"],
        "task_dep": ["clean_public"],
        "verbosity": 2,
        "clean": [],  # Don't clean these files by default.
    }
```