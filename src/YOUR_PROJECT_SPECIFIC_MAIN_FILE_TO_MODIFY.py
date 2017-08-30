#! /usr/bin/env python3
import sys, os

# YOU WILL DEFINITELY NEED TO MODIFY THESE PATHS
PROJECT_WITH_MACRO_OCCURRENCES_ROOT = "/Users/dustin/Sites/LfP/minimal-macros/test"
INNOCENT_MACROS_SRC_PATH = "/Users/dustin/Sites/LfP/minimal-macros/src"

# Below is my configuration for my (hopefully soon to be open source) project Structure Together.

# Assign a key ("build key") to paths of different build output js files, relative to PROJECT_WITH_MACRO_OCCURRENCES_ROOT
# Do NOT use keys that contain any of these substrings: -d --delete -e --expand -w --watch -o --overwrite -f --force
#
# All these files will be watched.
#
# For example mine are:
# dev for development
# scc for Simple-mode Closure Compiler
# acc for Advanced-mode Closure Compiler
RELPATHS_OF_FILES_WITH_MACRO_OCCURRENCES = {
    'dev': "structure-together-main.webpack-entry-chunk--dev.js",
	'scc': "structure-together-main.webpack-entry-chunk--scc.js",
    'acc': "structure-together-main.webpack-entry-chunk--acc.js"
}

abspaths = {k: os.path.join(PROJECT_WITH_MACRO_OCCURRENCES_ROOT, RELPATHS_OF_FILES_WITH_MACRO_OCCURRENCES[k]) for k in RELPATHS_OF_FILES_WITH_MACRO_OCCURRENCES.keys()}

config = {	
	'DEFAULT_OVERWRITE': False,
	'TS_MACRO_DEFS_PATH': os.path.join(PROJECT_WITH_MACRO_OCCURRENCES_ROOT, "structure_together_macros.ts"),
	'ABSPATHS_OF_FILES_WITH_MACRO_OCCURRENCES':  abspaths, 
	'DEFAULT_ACTIONS' : {
		'dev': 'expand',
		'scc': 'delete',
	    'acc': 'delete'
	},
	'INSERT_BUILD_TIME_CONSOLE_MSG' : {
		'dev': True, 'scc': True, 'acc': True
	}
}


if __name__ == "__main__":
	import sys
	sys.path.append(INNOCENT_MACROS_SRC_PATH)
	from minimal_macros_api_with_watch import start_processing
	start_processing(config, sys.argv)
