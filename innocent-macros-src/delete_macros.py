import sys, datetime, os

from constants import INSERT_CONSOLE_LOG_OF_BUILD_TIME
from common import *


def parse_macro_defs_file_to_macronames( macro_defs_file_path: str ) -> List[str]:
	macro_names = []
	def handle_single_macro_def(fnname, params_str, body_as_single_line):
		macro_names.append(fnname)
	for_each_macro_def( macro_defs_file_path, handle_single_macro_def )
	return macro_names

def run_macro_deletion(path_to_macro_defs,  path_to_js_needing_processing, outfile_path, key):
	filename = os.path.basename(path_to_js_needing_processing)
	# print("File: " + filename)

	starttime = perfcounter()
	jsstr = readfile_as_string(path_to_js_needing_processing)
	if not jsstr:
		return

	macronames = parse_macro_defs_file_to_macronames( path_to_macro_defs )

	macronames_together_then_paren = r"(?:" + r"|".join(macronames) + r")\("
	namespace_then_macronames_together_then_paren = r"(?:\w+\.)+" + macronames_together_then_paren

	macro_re = re.compile(namespace_then_macronames_together_then_paren,re.MULTILINE)
	
	outfile = open(outfile_path, 'w')

	deleted_macros = 0
	deleted_chars = 0

	nextwriteind = 0

	while True:
		match = macro_re.search(jsstr, nextwriteind)
		if not match:
			break

		macrostart = match.start()
		outfile.write('0') # sometimes need to insert a noop in minified code
		outfile.write(jsstr[nextwriteind:macrostart])

		next_after_openparen = match.end()
		closeparen = find_next_toplevel_in_str(jsstr, next_after_openparen, ')')
		if not closeparen:
			raise Exception
		nextwriteind = closeparen + 1

		deleted_chars += nextwriteind - macrostart + 2
		deleted_macros += 1
		# print(jsstr[macrostart:nextwriteind])

	outfile.write(jsstr[nextwriteind:])	
		
	curtime = datetime.datetime.now().strftime("%I:%M:%S")
	if INSERT_CONSOLE_LOG_OF_BUILD_TIME:  
		timestamp_print_command = "\nconsole.log('[{}] Build of {}');\n".format(filename, curtime);		
		outfile.write(timestamp_print_command);
	
	outfile.close()

	# print("[IM] {}: deleted {} lines (replaced with blank lines), {} milliseconds\n".format(curtime, deleted_lines, round(1000*(perfcounter() - starttime))))
	print("\t[IM] Deleted {num} macro occurrences, {time} ms ({chars} chars)".format(time=round(1000*(perfcounter() - starttime)), num=deleted_macros, chars=deleted_chars))

