import os
import sys
from settings import config

POSTS_DIR = config("POSTS_DIR")

def list_posts_subdirs():
    print(list(os.listdir(POSTS_DIR)))
    sys.stdout.flush()  # <<< Force output to appear when run as subprocess

if __name__ == "__main__":
    list_posts_subdirs()
