#! /usr/bin/env python3
# import subprocess, atexit
# from subprocess import Popen, PIPE


import os, time
from expand_macros import run_macro_expansion
# from delete_macros import run_macro_line_deletion
from delete_macros import run_macro_deletion

# disabled 2016/6/21 from constants import TS_IDENTITY_FNS_WITH_SIDE_EFFECTS_PATH,  

subprocesses = dict()

def polling(macro_defs_path, src_file_paths, fns_when_test_true, use_dot_out, force):
	while True:
		for key,path in src_file_paths.items():
			try:
				moddate = os.stat(path)[8] 
				if subprocesses[key] != moddate:
					subprocesses[key] = moddate
					fns_when_test_true[key](macro_defs_path, path, use_dot_out, force, key)
			except Exception as e:
				print("File not found for build {} at {}".format(key, path)) 
					
		time.sleep(.5)

def deletion_call_once(macro_defs_path, src_path, use_dot_out, force, key):
	run_macro_deletion(
		macro_defs_path, 
		src_path, 
		src_path + ".out" if use_dot_out else src_path,
		ignore_HAS_BEEN_PROCESSED_MARKER=force,
		key=key
	)

def expansion_call_once(macro_defs_path, src_path, use_dot_out, force, key):
	run_macro_expansion(
		macro_defs_path,
		src_path,
		src_path + ".out" if use_dot_out else src_path,
		ignore_HAS_BEEN_PROCESSED_MARKER=force,
		key=key
	)
	
def start_processing(config, args):
	production_mode = "-p" in args or "--production" in args
	dev_mode = "-d" in args or "--dev" in args
	watch_mode = "-w" in args or "--watch" in args

	# assert dev_mode or production_mode, "Must use -p (--production) or -d (--dev)"
	if not (dev_mode or production_mode):
		print("\n[IM] No '-p' or '-d' arg given, so using defaults config only to determine which files to expand vs. remove macros in.")

		fns = {k: (expansion_call_once if config['DEFAULT_MODES'][k] == '-d' else deletion_call_once) for k in config['DEFAULT_MODES'].keys()}
	elif dev_mode:
		fns = {k: expansion_call_once for k in config['DEFAULT_MODES'].keys()}
	else: 
		assert production_mode
		fns = {k: deletion_call_once for k in config['DEFAULT_MODES'].keys()}

	use_dot_out = ".out" in args

	force = "force" in args
	if force:
		print("force used")

	for key in config['PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS'].keys():
		subprocesses[key] = 0


	for key,path in config['PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS'].items():
		print("\n[IM] Processing key " + key)
		# try:
		if production_mode or config['DEFAULT_MODES'][key] == '-p':
			deletion_call_once(config['TS_MACRO_DEFS_PATH'], path, use_dot_out, force, key)
		else:
			expansion_call_once(config['TS_MACRO_DEFS_PATH'], path, use_dot_out, force, key)

	if watch_mode:
		print("\n[IM] Starting watch mode")
		polling(config['TS_MACRO_DEFS_PATH'],config['PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS'], fns, use_dot_out, force)

		# if production_mode or config['DEFAULT_MODES'][key] == '-p':
		# 	print("[IM] Starting prod watch mode for " + path)
			
		# else:
		# 	print("[IM] Starting dev watch mode for " + path)
		# 	polling(config['TS_MACRO_DEFS_PATH'], config['PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS'], expansion_call_once, use_dot_out, force)
					
		# except Exception as e:
			# print("File not found or other exception for: {}".format(path))
			# print(e) 
		
	# if watch_mode:
	# 	print("[MCM] Starting watch mode")
	# 	polling(config['TS_MACRO_DEFS_PATH'],config['PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS'], 
	# 		deletion_call_once, use_dot_out, force)


	# if production_mode:
	# 	print("\n[MCM] Production mode")	
	# 	for path in config['PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS']:
	# 		deletion_call_once(config['TS_MACRO_DEFS_PATH'], path, use_dot_out, force)
		
	# 	if watch_mode:
	# 		print("[MCM] Starting watch mode")
	# 		polling(config['TS_MACRO_DEFS_PATH'],config['PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS'], 
	# 			deletion_call_once, use_dot_out, force)

	# elif dev_mode:
	# 	print("\n[MCM] Dev mode.")
	# 	for path in config['PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS']:
	# 		try:
	# 			expansion_call_once(config['TS_MACRO_DEFS_PATH'], path, use_dot_out, force)
	# 		except Exception as e:
	# 			print("File not found at {}".format(path)) 

	# 	if watch_mode:
	# 		print("[MCM] Starting watch mode")
	# 		polling(config['TS_MACRO_DEFS_PATH'], config['PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS'], 				
	# 			expansion_call_once, use_dot_out, force)


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
