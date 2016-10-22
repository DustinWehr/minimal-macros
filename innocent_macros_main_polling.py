#! /usr/bin/env python3
# import subprocess, atexit
# from subprocess import Popen, PIPE


import sys, os, time
from expand_macros import run_macro_expansion
from delete_macros import run_macro_deletion

from constants import MACROS_PROJECT_ROOT, EXPANSION_SCRIPT_NAME, DELETION_SCRIPT_NAME
from constants import TS_MACRO_DEFS_PATH, SRC_WITH_MACRO_OCCURRENCES_TO_PROCESS, PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS
# disabled 2016/6/21 from constants import TS_IDENTITY_FNS_WITH_SIDE_EFFECTS_PATH,  

# out_file_path = SRC_WITH_MACRO_OCCURRENCES_TO_PROCESS + ".out"
def out_file_path(in_path): 
	return in_path + (".out" if ".out" in sys.argv else "")

production_mode = "-p" in sys.argv or "--production" in sys.argv
dev_mode = "-d" in sys.argv or "--dev" in sys.argv
watch_mode = "-w" in sys.argv or "--watch" in sys.argv

assert dev_mode or production_mode, "Must use -p (--production) or -d (--dev)"

FORCE = "force" in sys.argv

subprocesses = dict()
for path in PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS:
	subprocesses[path] = 0

def polling(file_paths, when_test_true):
	while True:
		for path in file_paths:
			moddate = os.stat(path)[8] 
			if subprocesses[path] != moddate:
				subprocesses[path] = moddate
				when_test_true(path)
		time.sleep(.5)

def deletion_call_once(src_path):
	run_macro_deletion(
		TS_MACRO_DEFS_PATH, 
		src_path, 
		out_file_path(src_path),
		ignore_HAS_BEEN_PROCESSED_MARKER=FORCE
	)

def expansion_call_once(src_path):
	run_macro_expansion(
		TS_MACRO_DEFS_PATH,
		src_path,
		out_file_path(src_path),
		ignore_HAS_BEEN_PROCESSED_MARKER=FORCE
	)
	

if production_mode:
	# print("\n[MCM] Production mode")
	print("\n[MCM] Production mode")	
	for path in PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS:
		deletion_call_once(path)
	
	if watch_mode:
		print("[MCM] Starting watch mode")
		polling(PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS, deletion_call_once)
		# for path in PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS:	
			# watch_call(path, DELETION_SCRIPT_NAME)
elif dev_mode:
	# print("\n[MCM] Dev mode")
	print("\n[MCM] Dev mode.")
	for path in PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS:
		expansion_call_once(path)

	if watch_mode:
		print("[MCM] Starting watch mode")
		polling(PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS, expansion_call_once)
		# for path in PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS:
			# watch_call(path, EXPANSION_SCRIPT_NAME)			
else:
	raise Exception("Must use -p (--production) or -d (--dev)")

# atexit.register(kill_subprocesses)

# for p in subprocesses:
# 	p.wait()			


# sys.exit()

# os.wait()


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
