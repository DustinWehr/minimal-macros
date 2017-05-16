import os, time
from expand_macros import run_macro_expansion
from delete_macros import run_macro_deletion


approx_last_mod_time = dict()
skipped_notif = dict()

def polling(macro_defs_path, src_file_paths, fns_when_test_true, use_dot_out, force):
	for key,path in src_file_paths.items():
		approx_last_mod_time[key] = os.stat(path).st_mtime_ns
		skipped_notif[key] = False

	while True:
		for key,path in src_file_paths.items():
			try:
				assert key in approx_last_mod_time # should happen in start_processing	
				file_last_mod_time = os.stat(path).st_mtime_ns
				difference = abs(approx_last_mod_time[key] - file_last_mod_time)
				if difference > 0:
					# print(approx_last_mod_time[key])
					# print(file_last_mod_time)
					print("[IM] Processing build '{}'.".format(key))
					fns_when_test_true[key](macro_defs_path, path, use_dot_out, force, key)
					approx_last_mod_time[key] = file_last_mod_time
					skipped_notif[key] = False					
				else:
					if not skipped_notif[key]:
						print("[IM] Mod times match for build '{}'. Skipping.".format(key))
						skipped_notif[key] = True
					# approx_last_mod_time[key] = time.time()					
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
	if "-h" in args or "--help" in args or "help" in args:
		print("[IM] Usage:")
		print('"<your custom python main script name> [<build key>] <options>" - See the sample file innocent_macros_st.py and/or readme.md if you don\'t know what the first two parts are for.')		
		print('"-d" or "--delete" - Delete macros in all the watched files, overiding your config object\'s DEFAULT_ACTIONS')	
		print('"-e" or "--expand" - Expand macros in all the watched files, overiding your config object\'s DEFAULT_ACTIONS')
		print('"-w" or "--watch" - Watch the files in your config object for change. When a file changes, repeat the initial actions performed on it.')	
		print('"-o" or "--overwrite" - Overwrite the input file with the macro expanded/deleted file. Otherwise, will append ".out" to the output filename.')
		# print('"-f" or "--force" - Ignore modification time of files on first run of this process. On subsequent runs of this same process, modification times are never ignored (since otherwise would run over and over again).')
		return

	all_builds_delete_mode = "-d" in args or "--delete" in args
	all_builds_expand_mode = '-e' in args or "--expand" in args
	watch_mode = "-w" in args or "--watch" in args

	assert not (all_builds_delete_mode and all_builds_expand_mode)	

	if not (all_builds_expand_mode or all_builds_delete_mode):
		print("\n[IM] No '-d' ('--delete') or '-e' ('--expand') arg given, so using your config object to determine which files to expand/delete macros in.")		
		if not 'DEFAULT_ACTIONS' in config:
			print("\n[IM] ...but your config object does contain a 'DEFAULT_ACTIONS' key, so can't do that. Exiting.")

	use_dot_out = not ( "-o" in args or '--overwrite' in args)

	force = "--force" in args
	if force:
		print("[IM] force used")


	for key,path in config['ABSPATHS_OF_FILES_WITH_MACRO_OCCURRENCES'].items():
		print("[IM] Processing build '{}'".format(key))
		if all_builds_delete_mode or (not all_builds_expand_mode and config['DEFAULT_ACTIONS'][key] == 'delete'):
			deletion_call_once(config['TS_MACRO_DEFS_PATH'], path, use_dot_out, force, key)
		else:
			assert all_builds_expand_mode or (not all_builds_delete_mode and config['DEFAULT_ACTIONS'][key] == 'expand')
			expansion_call_once(config['TS_MACRO_DEFS_PATH'], path, use_dot_out, force, key)
		approx_last_mod_time[key] = time.time()

	if watch_mode:		
		if all_builds_expand_mode:
			fns = {k: expansion_call_once for k in config['DEFAULT_ACTIONS'].keys()}
		elif all_builds_delete_mode: 			
			fns = {k: deletion_call_once for k in config['DEFAULT_ACTIONS'].keys()}
		else:
			fns = {k: expansion_call_once if config['DEFAULT_ACTIONS'][k] == 'expand' else 
					 (deletion_call_once if config['DEFAULT_ACTIONS'] == 'delete' else None) for k in config['DEFAULT_ACTIONS'].keys()}

		print("\n[IM] Starting watch mode")
		polling(config['TS_MACRO_DEFS_PATH'],config['ABSPATHS_OF_FILES_WITH_MACRO_OCCURRENCES'], fns, use_dot_out, False)
		