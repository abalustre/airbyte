#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from base_python.entrypoint import launch
from source_file_tc import SourceFileTC

if __name__ == "__main__":
    source = SourceFileTC()
    launch(source, sys.argv[1:])
