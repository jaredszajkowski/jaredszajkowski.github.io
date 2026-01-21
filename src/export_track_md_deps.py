from pathlib import Path

def export_track_md_deps(
    dep_file: Path, 
    md_filename: str, 
    content: str,
    text_or_python: str,
) -> None:
    
    """
    Export Markdown content to a file and track it as a dependency.

    This function writes the provided content to the specified Markdown file and 
    appends the filename to the given dependency file (typically `index_dep.txt`).
    This is useful in workflows where Markdown fragments are later assembled 
    into a larger document (e.g., a Hugo `index.md`).

    Parameters
    ----------
    dep_file : Path
        Path to the dependency file that tracks Markdown fragment filenames.
    md_filename : str
        The name of the Markdown file to export.
    content : str
        The Markdown-formatted content to write to the file.
    text_or_python : str
        Indicates whether the content is plain text or Python code for proper formatting.

    Returns
    -------
    None

    Example
    -------
    >>> export_track_md_deps(Path("index_dep.txt"), "01_intro.md", "# Introduction\n...")
    ✅ Exported and tracked: 01_intro.md
    """
    
    if text_or_python == "python":
        Path(md_filename).write_text(f"```python\n{content}\n```")
    elif text_or_python == "text":
        Path(md_filename).write_text(f"```text\n{content}\n```")
    elif text_or_python == "markdown":
        Path(md_filename).write_text(f"{content}")
    else:
        raise ValueError("text_or_python must be either 'text', 'python', or 'markdown'.")

    with dep_file.open("a") as f:
        f.write(md_filename + "\n")
    print(f"✅ Exported and tracked: {md_filename}")