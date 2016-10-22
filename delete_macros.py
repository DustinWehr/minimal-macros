#! /usr/bin/env python3
import sys, re, datetime, time
from common import *

from constants import HAS_BEEN_PROCESSED_MARKER__PRODUCTION, INSERT_CONSOLE_LOG_OF_BUILD_TIME
from constants import NON_WORD_CHAR_OR_START_OF_STRING, RE_FOR_STUFF_BEFORE_MACRO_NAME

def parse_macro_defs_file_to_macronames( macro_defs_file_path ):
	macros = {}

	def handle_single_macro_def(fnname, params_str, body_as_single_line):
		macros[fnname] = "whole-line"

	for_each_macro_def( macro_defs_file_path, handle_single_macro_def )

	return macros


def run_macro_deletion(path_to_macro_defs,  path_to_js_needing_processing, outfile_path, ignore_HAS_BEEN_PROCESSED_MARKER=False):
	# assert False, "TODO: this doesn't work because "
	print("File: " + path_to_filename(path_to_js_needing_processing))

	starttime = perfcounter()
	jslines = maybe_readlines_and_maybe_modify_first(
		path_to_js_needing_processing, 
		HAS_BEEN_PROCESSED_MARKER__PRODUCTION,
		ignore_HAS_BEEN_PROCESSED_MARKER )
	if jslines is None:
		return

	macros = parse_macro_defs_file_to_macronames( path_to_macro_defs )
	
	macronames = []

	for k in macros:
		if macros[k] == "whole-line":
			macronames.append(k)
		else:
			raise Error	
	# macronames = macros.keys()

	# print("macronames:", macronames)
	# print("identitynames:", identitynames)

	# macronames_with_paren = map(lambda x: x + r"\(", macronames)
	# macronames_together = "(" + "|".join(macronames_with_paren) + ")"	
	macronames_together_then_paren = r"(" + r"|".join(macronames) + r")\("
	
	
	# Mar 16
	macro_re_str = macronames_together_then_paren + r"(?:.*)\)\s*;\s*$"
	# macro_re_str = r"^(?:\s*)" + macronames_together_then_paren + r"(?:.*)\)\s*;\s*$"
	

	macro_re = re.compile(macro_re_str)
	

	# NTS: I gave it a a good try at making "for line in file" work with inserting console log. 
	# Not worth trying any more. See ABOUT PERFORMANCE.txt
	if INSERT_CONSOLE_LOG_OF_BUILD_TIME:
		last_line_num_to_process = find_spot_for_console_msg(jslines)
	else:
		last_line_num_to_process = len(jslines) - 1

	print("[MCM] Read {} js lines.".format(len(jslines)))	

	outfile = open(outfile_path, 'w')

	deleted_lines = 0
	line_num = 0

	while line_num <= last_line_num_to_process:		
		line = jslines[line_num]
		line_ind = 0
		while True:
			if line_ind == 0:
				match = macro_re.search(line)
				# match = macro_re.match(line)  # Mar 16
				if match:
					fnname = match.group(1)
					# assert fnname != "nt"
					if macros[fnname] == "whole-line":
						deleted_lines += 1
						outfile.write("\n")
						line_num += 1
						# continue
						break
					else:
						raise Exception	
			
			# if neither matched	
			# begin simple version
			# outfile.write(line)
			# end simple version
			outfile.write(line[line_ind:])

			line_num += 1
			break
		
	
	curtime = datetime.datetime.now().strftime("%I:%M:%S")
	if INSERT_CONSOLE_LOG_OF_BUILD_TIME:  
		timestamp_print_command = "if(window.structure_together.dev_mode) {{ console.log('[{}] Build of {}'); }}\n".format(path_to_filename(path_to_js_needing_processing), curtime);
		# timestamp_print_command = "if(window.structure_together.dev_mode) { console.log('[MCM] Build of {}'); }\n".format(curtime);
		outfile.write(timestamp_print_command);

		for line in jslines[last_line_num_to_process + 1: len(jslines)]:
			outfile.write(line)
	
	outfile.close()

	# print("[MCM] {}: deleted {} lines (replaced with blank lines), {} milliseconds\n".format(curtime, deleted_lines, round(1000*(perfcounter() - starttime))))
	print("[MCM] {time} ms, deleted {num} lines (replaced with blank lines)\n".format(time=round(1000*(perfcounter() - starttime)), num=deleted_lines))

	

if __name__ == '__main__':
	# print(sys.argv)
	assert 6 <= len(sys.argv) <= 7, "[MCM] 4 or 5 arguments are required to command-line invocation of delete_macros.py"
	if len(sys.argv) == 6:
		run_macro_deletion(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
	elif len(sys.argv) == 7:  
		run_macro_deletion(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

