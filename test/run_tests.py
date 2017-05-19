#! /usr/bin/env python3
import sys
sys.path.extend(["../innocent_macros_src", "./innocent_macros_src"])
import YOUR_PROJECT_SPECIFIC_MAIN_FILE_TO_MODIFY as script
import innocent_macros_api_with_watch as lib

lib.start_processing(script.config, [])

