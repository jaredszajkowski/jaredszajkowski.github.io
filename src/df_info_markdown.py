import io
import pandas as pd

def df_info_markdown(df):
    """Convert outputs to markdown for df.info(), df.head(), and df.tail()."""
    buffer = io.StringIO()

    # Capture df.info() output
    df.info(buf=buffer)
    info_str = buffer.getvalue()

    # Get head as markdown
    head_str = df.head().to_markdown()

    # Get tail as markdown
    tail_str = df.tail().to_markdown()

    markdown = []
    markdown.append("```text")
    markdown.append("The columns, shape, and data types are:\n")
    markdown.append(info_str)
    markdown.append("```")
    markdown.append("\nThe first 5 rows are:\n")
    markdown.append(head_str)
    markdown.append("\nThe last 5 rows are:\n")
    markdown.append(tail_str)
    return "\n".join(markdown)