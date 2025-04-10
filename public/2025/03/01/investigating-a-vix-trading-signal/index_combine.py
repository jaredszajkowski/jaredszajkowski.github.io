from pathlib import Path

# This script combines the content of multiple markdown files into a single index.md file.

# Wrap the paths as Path objects
temp_index_path = Path("index_temp.md")
final_index_path = Path("index.md")
df_info_path = Path("01_DF_Info.md")
vix_stats_path = Path("02_VIX_Stats.md")
vix_deciles_path = Path("03_VIX_Deciles.md")

# Read existing files
temp_index_content = temp_index_path.read_text()
df_info_content = df_info_path.read_text()
vix_stats_content = vix_stats_path.read_text()
vix_deciles_content = vix_deciles_path.read_text()

# Replace placeholders
final_index_content = temp_index_content
final_index_content = final_index_content.replace("<!-- INSERT_DF_INFO_HERE -->", df_info_content)
final_index_content = final_index_content.replace("<!-- INSERT_VIX_STATS_HERE -->", vix_stats_content)
final_index_content = final_index_content.replace("<!-- INSERT_VIX_DECILES_HERE -->", vix_deciles_content)

# Write final index.md
final_index_path.write_text(final_index_content)