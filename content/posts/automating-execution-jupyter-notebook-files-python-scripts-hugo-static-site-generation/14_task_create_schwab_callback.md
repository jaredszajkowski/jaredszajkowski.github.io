```python
def task_create_schwab_callback():
    """Create a Schwab callback URL by creating /static/schwab_callback/index.html and placing the html code in it"""
    def create_callback():
        callback_path = STATIC_DIR / "schwab_callback" / "index.html"
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
        "task_dep": ["copy_projects_research_exports"],
        "verbosity": 2,
        "clean": [],  # Don't clean these files by default.
    }
```