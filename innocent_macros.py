#! /usr/bin/env python3
# import subprocess, atexit
# from subprocess import Popen, PIPE


import os, time
from expand_macros import run_macro_expansion
from delete_macros import run_macro_deletion

# disabled 2016/6/21 from constants import TS_IDENTITY_FNS_WITH_SIDE_EFFECTS_PATH,  

subprocesses = dict()

def polling(macro_defs_path, src_file_paths, when_test_true, use_dot_out=False, force=False):
	while True:
		for path in src_file_paths:
			moddate = os.stat(path)[8] 
			if subprocesses[path] != moddate:
				subprocesses[path] = moddate
				when_test_true(macro_defs_path, path, use_dot_out, force)
		time.sleep(.5)

def deletion_call_once(macro_defs_path, src_path, use_dot_out=False, force=False):
	run_macro_deletion(
		macro_defs_path, 
		src_path, 
		src_path + ".out" if use_dot_out else src_path,
		ignore_HAS_BEEN_PROCESSED_MARKER=false
	)

def expansion_call_once(macro_defs_path, src_path, use_dot_out=False, force=False):
	run_macro_expansion(
		macro_defs_path,
		src_path,
		src_path + ".out" if use_dot_out else src_path,
		ignore_HAS_BEEN_PROCESSED_MARKER=force
	)
	
def start_expansion(config, args):
	production_mode = "-p" in args or "--production" in args
	dev_mode = "-d" in args or "--dev" in args
	watch_mode = "-w" in args or "--watch" in args

	assert dev_mode or production_mode, "Must use -p (--production) or -d (--dev)"

	use_dot_out = ".out" in args

	force = "force" in args
	if force:
		print("force used")

	for path in config['PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS']:
		subprocesses[path] = 0

	if production_mode:
		print("\n[MCM] Production mode")	
		for path in config['PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS']:
			deletion_call_once(config['TS_MACRO_DEFS_PATH'], path, use_dot_out, force)
		
		if watch_mode:
			print("[MCM] Starting watch mode")
			polling(config['TS_MACRO_DEFS_PATH'],config['PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS'], 
				deletion_call_once, use_dot_out, force)

	elif dev_mode:
		print("\n[MCM] Dev mode.")
		for path in config['PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS']:
			expansion_call_once(config['TS_MACRO_DEFS_PATH'], path, use_dot_out, force)

		if watch_mode:
			print("[MCM] Starting watch mode")
			polling(config['TS_MACRO_DEFS_PATH'], config['PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS'], 
				expansion_call_once, use_dot_out, force)


if __name__ == "__main__":
    import sys
    innocent_macros(int(sys.argv[1]))    


# OUT-OF-DATE** DOCS:
# Work flow:
# This script with parameter "watch" starts a file watcher W for F1 = TS_MACRO_DEFS_PATH and F2 = SRC_WITH_MACRO_OCCURRENCES_TO_PROCESS
# When max_compat_macros_main.py runs:
#   Reads F1 and F2
#   script looks at the (FIRST for (b), LAST for (a)) line of F2 to see if it's "// MACROS EXPANDED". If so, it finishes.
#   otherwise, it either:
#     (a) -appends the line "// MACROS EXPANDED" to F2, and then
#         -uses Python's FileInput class with backup and inplace parameters to do substitutions in-place, or:
#     (b) (this is probably just as fast since I've already read the whole file, and due to how harddrives work)
#         -open( ,LogTypes.rt) the file F2, read the lines, then close() it.
#         -init output string to "// MACROS EXPANDED\n".
#         -do the substititions and append them to the output string.
#         -open( ,'wt') the file F2 (write as text, which truncates), write() the output string, then close() the file.
# No need to create backup since the .js file is generated anyway.
