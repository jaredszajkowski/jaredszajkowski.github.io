import pandas as pd

def sm_ols_summary_markdown(result, file_path):
    """
    Convert a statsmodels summary into markdown and save it.
    """
    # # Extract the main table and the additional stats table
    # summ = result.summary()

    # # statsmodels Summary() tables are in .tables list
    # tables = []
    # for table in summ.tables:
    #     df = pd.DataFrame(table.data[1:], columns=table.data[0])
    #     tables.append(df.to_markdown(index=False))

    # # Join markdown tables with spacing
    # md = "\n\n".join(tables)

    # # Write out
    # with open(file_path, "w") as f:
    #     f.write(md)

    # return md

    text = result.summary().as_text()
    md = f"```\n{text}\n```"
    with open(file_path, "w") as f:
        f.write(md)
    return md
