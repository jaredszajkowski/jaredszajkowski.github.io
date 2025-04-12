"""
build_index.py

This script combines Markdown fragments into a Hugo-compatible index.md file
by replacing placeholders in index_temp.md based on index_dependencies.txt.
"""

from pathlib import Path

def build_index():
    temp_index_path = Path("index_temp.md")
    final_index_path = Path("index.md")
    dependencies_path = Path("index_dep.txt")

    # Read the index template
    if not temp_index_path.exists():
        raise FileNotFoundError("Missing index_temp.md")

    temp_index_content = temp_index_path.read_text()

    # Read dependency list
    if not dependencies_path.exists():
        raise FileNotFoundError("Missing index_dependencies.txt")

    with dependencies_path.open("r") as f:
        markdown_files = [line.strip() for line in f if line.strip()]

    # Replace placeholders for each dependency
    final_index_content = temp_index_content
    for md_file in markdown_files:
        # placeholder = f"<!-- INSERT_{Path(md_file).stem.upper()}_HERE -->"
        placeholder = f"<!-- INSERT_{Path(md_file).stem}_HERE -->"
        if Path(md_file).exists():
            content = Path(md_file).read_text()
            final_index_content = final_index_content.replace(placeholder, content)
        else:
            print(f"⚠️  Warning: {md_file} not found, skipping placeholder {placeholder}")
            final_index_content = final_index_content.replace(placeholder, f"*{md_file} not found*")

    # Write final index.md
    final_index_path.write_text(final_index_content)
    print("✅ index.md successfully built!")

if __name__ == "__main__":
    build_index()



# """
# build_index.py

# This script combines multiple Markdown fragments into a single Hugo-compatible index.md file
# by replacing predefined placeholders in a template file (index_temp.md).
# """

# from pathlib import Path



# def build_index():
#     # Define paths
#     temp_index_path = Path("index_temp.md")
#     final_index_path = Path("index.md")
#     df_info_path = Path("01_DF_Info.md")
#     vix_stats_path = Path("02_VIX_Stats.md")
#     vix_deciles_path = Path("03_VIX_Deciles.md")

#     # Read markdown components
#     temp_index_content = temp_index_path.read_text()
#     df_info_content = df_info_path.read_text()
#     vix_stats_content = vix_stats_path.read_text()
#     vix_deciles_content = vix_deciles_path.read_text()

#     # Replace placeholders
#     final_index_content = temp_index_content
#     final_index_content = final_index_content.replace("<!-- INSERT_DF_INFO_HERE -->", df_info_content)
#     final_index_content = final_index_content.replace("<!-- INSERT_VIX_STATS_HERE -->", vix_stats_content)
#     final_index_content = final_index_content.replace("<!-- INSERT_VIX_DECILES_HERE -->", vix_deciles_content)

#     # Write final output
#     final_index_path.write_text(final_index_content)
#     print("✅ index.md successfully built!")

# if __name__ == "__main__":
#     build_index()
