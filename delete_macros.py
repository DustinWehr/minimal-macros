#! /usr/bin/env python3
import sys, datetime
from typing import *
from common import *

from constants import HAS_BEEN_PROCESSED_MARKER__PRODUCTION, INSERT_CONSOLE_LOG_OF_BUILD_TIME

def parse_macro_defs_file_to_macronames( macro_defs_file_path: str ) -> List[str]:
	macro_names = []
	def handle_single_macro_def(fnname, params_str, body_as_single_line):
		macro_names.append(fnname)
	for_each_macro_def( macro_defs_file_path, handle_single_macro_def )
	return macro_names

def run_macro_deletion(path_to_macro_defs,  path_to_js_needing_processing, outfile_path, ignore_HAS_BEEN_PROCESSED_MARKER, key):
	# assert False, "TODO: this doesn't work because "
	filename = path_to_filename(path_to_js_needing_processing)
	# print("File: " + filename)

	starttime = perfcounter()
	jsstr = maybe_readfile_as_string_and_insert_marker(
		path_to_js_needing_processing, 
		HAS_BEEN_PROCESSED_MARKER__PRODUCTION,
		ignore_HAS_BEEN_PROCESSED_MARKER,
		key )
	if not jsstr:
		return

	macros = parse_macro_defs_file_to_macronames( path_to_macro_defs )
	
	macronames = []

	for k in macros:
		if macros[k] == "whole-line":
			macronames.append(k)
		else:
			print("todo: not hard to make this work with non-whole-line macros")
			raise Exception

	# print("macronames:", macronames)

	macronames_together_then_paren = r"(?:" + r"|".join(macronames) + r")\("
	namespace_then_macronames_together_then_paren = r"(?:\w+\.)+" + macronames_together_then_paren

	macro_re = re.compile(namespace_then_macronames_together_then_paren,re.MULTILINE)
	
	outfile = open(outfile_path, 'w')

	deleted_macros = 0
	deleted_chars = 0
	line_num = 0

	nextwriteind = 0

	while True:
		match = macro_re.search(jsstr, nextwriteind)
		if not match:
			break

		# fnname = match.group(1)
		macrostart = match.start()
		# outfile.write('noop()')
		outfile.write('0')
		outfile.write(jsstr[nextwriteind:macrostart])

		next_after_openparen = match.end()
		closeparen = find_next_toplevel_in_str(jsstr, next_after_openparen, ')')
		if not closeparen:
			raise Exception
		# if jsstr[closeparen+1] == ';':
			# nextwriteind = closeparen + 2
		# else:
		nextwriteind = closeparen + 1

		deleted_chars += nextwriteind - macrostart + 2
		deleted_macros += 1
		# print(jsstr[macrostart:nextwriteind])

	outfile.write(jsstr[nextwriteind:])	
		
	curtime = datetime.datetime.now().strftime("%I:%M:%S")
	if INSERT_CONSOLE_LOG_OF_BUILD_TIME:  
		timestamp_print_command = "\nconsole.log('[{}] Build of {}');\n".format(filename, curtime);
		# timestamp_print_command = "if(window.structure_together.dev_mode) { console.log('[MCM] Build of {}'); }\n".format(curtime);
		outfile.write(timestamp_print_command);
	
	outfile.close()

	# print("[MCM] {}: deleted {} lines (replaced with blank lines), {} milliseconds\n".format(curtime, deleted_lines, round(1000*(perfcounter() - starttime))))
	print("[MCM] {time} ms, deleted {num} macro occurrences ({chars})\n".format(time=round(1000*(perfcounter() - starttime)), num=deleted_macros, chars=deleted_chars))



	

if __name__ == '__main__':
	# print(sys.argv)
	assert 6 <= len(sys.argv) <= 7, "[MCM] 4 or 5 arguments are required to command-line invocation of delete_macros.py"
	if len(sys.argv) == 6:
		run_macro_deletion(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
	elif len(sys.argv) == 7:  
		run_macro_deletion(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])





