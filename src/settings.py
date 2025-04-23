"""
Load project configurations from .env files.
Provides easy access to paths and credentials used in the project.
Meant to be used as an imported module.

If `settings.py` is run on its own, it will create the appropriate
directories.

For information about the rationale behind decouple and this module,
see https://pypi.org/project/python-decouple/

Note that decouple mentions that it will help to ensure that
the project has "only one configuration module to rule all your instances."
This is achieved by putting all the configuration into the `.env` file.
You can have different sets of variables for difference instances,
such as `.env.development` or `.env.production`. You would only
need to copy over the settings from one into `.env` to switch
over to the other configuration, for example.
"""

from pathlib import Path
from platform import system
from decouple import config as _config
from pandas import to_datetime

def get_os():
    os_name = system()
    if os_name == "Windows":
        return "windows"
    elif os_name == "Darwin":
        return "nix"
    elif os_name == "Linux":
        return "nix"
    else:
        return "unknown"

# def if_relative_make_abs(path):
def if_relative_make_abs(base_dir, path):
    """If a relative path is given, make it absolute, assuming
    that it is relative to the project root directory (BASE_DIR)

    Example
    -------
    ```
    >>> if_relative_make_abs(Path('_data'))
    WindowsPath('C:/Users/jdoe/GitRepositories/blank_project/_data')

    >>> if_relative_make_abs(Path("C:/Users/jdoe/GitRepositories/blank_project/_output"))
    WindowsPath('C:/Users/jdoe/GitRepositories/blank_project/_output')
    ```
    """
    path = Path(path)
    if path.is_absolute():
        abs_path = path.resolve()
    else:
        # abs_path = (d["BASE_DIR"] / path).resolve()
        abs_path = (base_dir / path).resolve()
    return abs_path

# Initialize the dictionary to hold all the settings
d = {}

# Get the OS type
d["OS_TYPE"] = get_os()

# Absolute path to root directory of the project
d["BASE_DIR"] = Path(__file__).absolute().parent.parent

# fmt: off
## Other .env variables
# d["START_DATE"] = _config("START_DATE", default="1930-01-01", cast=to_datetime)
# d["END_DATE"] = _config("END_DATE", default="2024-01-01", cast=to_datetime)
# d["PIPELINE_DEV_MODE"] = _config("PIPELINE_DEV_MODE", default=True, cast=bool)
# d["PIPELINE_THEME"] = _config("PIPELINE_THEME", default="pipeline")

## Paths
d["CONTENT_DIR"] = if_relative_make_abs(d["BASE_DIR"], _config('CONTENT_DIR', default=Path('content'), cast=Path))
d["POSTS_DIR"] = if_relative_make_abs(d["BASE_DIR"], _config('POSTS_DIR', default=Path('content/post'), cast=Path))
d["PAGES_DIR"] = if_relative_make_abs(d["BASE_DIR"], _config('PAGES_DIR', default=Path('content/page'), cast=Path))
d["PUBLIC_DIR"] = if_relative_make_abs(d["BASE_DIR"], _config('PUBLIC_DIR', default=Path('public'), cast=Path))
d["SOURCE_DIR"] = if_relative_make_abs(d["BASE_DIR"], _config('SOURCE_DIR', default=Path('src'), cast=Path))
d["DATA_DIR"] = if_relative_make_abs(d["BASE_DIR"], _config('DATA_DIR', default=Path('data'), cast=Path))

# External Paths
quant_finance_research_base_directory = "/home/jared/Cloud_Storage/Dropbox/Quant_Finance_Research"
d["QUANT_FINANCE_RESEARCH_BASE_DIR"] = Path(str(quant_finance_research_base_directory)).absolute()
d["QUANT_FINANCE_RESEARCH_SOURCE_DIR"] = if_relative_make_abs(d["QUANT_FINANCE_RESEARCH_BASE_DIR"], _config('QUANT_FINANCE_RESEARCH_SOURCE_DIR', default=Path('src'), cast=Path))

# # Print the dictionary to check the values
# for key, value in d.items():
#     print(f"{key}: {value}")

# fmt: on


# ## Name of Stata Executable in path
# if d["OS_TYPE"] == "windows":
#     d["STATA_EXE"] = _config("STATA_EXE", default="StataMP-64.exe")
# elif d["OS_TYPE"] == "nix":
#     d["STATA_EXE"] = _config("STATA_EXE", default="stata-mp")
# else:
#     raise ValueError("Unknown OS type")


def config(*args, **kwargs):
    key = args[0]
    default = kwargs.get("default", None)
    cast = kwargs.get("cast", None)
    if key in d:
        var = d[key]
        if default is not None:
            raise ValueError(
                f"Default for {key} already exists. Check your settings.py file."
            )
        if cast is not None:
            # Allows for re-emphasizing the type of the variable
            # But does not allow for changing the type of the variable
            # if the variable is defined in the settings.py file
            if type(cast(var)) is not type(var):
                raise ValueError(
                    f"Type for {key} is already set. Check your settings.py file."
                )
    else:
        # If the variable is not defined in the settings.py file,
        # then fall back to using decouple normally.
        var = _config(*args, **kwargs)
    return var


def create_dirs():
    ## If they don't exist, create the _data and _output directories
    d["CONTENT_DIR"].mkdir(parents=True, exist_ok=True)
    d["PAGES_DIR"].mkdir(parents=True, exist_ok=True)
    d["POSTS_DIR"].mkdir(parents=True, exist_ok=True)
    d["PUBLIC_DIR"].mkdir(parents=True, exist_ok=True)
    d["SOURCE_DIR"].mkdir(parents=True, exist_ok=True)
    d["DATA_DIR"].mkdir(parents=True, exist_ok=True)
    # (d["BASE_DIR"] / "_docs").mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    create_dirs()
