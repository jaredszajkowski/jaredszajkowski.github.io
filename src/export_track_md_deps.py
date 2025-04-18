from pathlib import Path

def export_track_md_deps(dep_file, md_filename: str, content: str):
    """Export markdown and append to index_dependencies.txt"""
    Path(md_filename).write_text(content)
    with dep_file.open("a") as f:
        f.write(md_filename + "\n")
    print(f"✅ Exported and tracked: {md_filename}")