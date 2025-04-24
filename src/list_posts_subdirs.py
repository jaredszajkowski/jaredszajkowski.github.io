import os
import sys
from settings import config

# Get the directory where post subdirectories are stored
POSTS_DIR = config("POSTS_DIR")

def list_posts_subdirs() -> None:
    
    """
    List the names of subdirectories in the configured POSTS_DIR.

    This function prints the contents of the POSTS_DIR to stdout. It is 
    particularly useful when running in a subprocess or automation tool 
    where stdout may need to be explicitly flushed.

    The POSTS_DIR path is retrieved from the project configuration using
    `config("POSTS_DIR")`.

    Returns:
    --------
    None

    Example:
    --------
    >>> list_posts_subdirs()
    ['post1', 'post2', 'post3']
    """
    
    print(list(os.listdir(POSTS_DIR)))
    sys.stdout.flush()  # Ensures output is immediately visible in subprocesses

if __name__ == "__main__":
    list_posts_subdirs()
