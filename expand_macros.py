#! /usr/bin/env python

import sys, datetime, time, re
from string import Formatter
from typing import List, Dict

from common import *
from WarningMsg import WarningMsg

from constants import VERBOSE_DEFAULT, ST_ROOT
from constants import HAS_BEEN_PROCESSED_MARKER__DEV, INSERT_CONSOLE_LOG_OF_BUILD_TIME
from constants import END_BLOCK_COMMENT_RE, RE_FOR_STUFF_BEFORE_MACRO_NAME

from macro_defn_datastructures import MacroDefn

def parse_macro_defs_file_to_substitution_objects( macro_defs_file_path, verbose = VERBOSE_DEFAULT ):
    macros = {}

    def handle_single_macro_def(fnname, params_str, body_as_single_line):
        macros[fnname] = MacroDefn(fnname, params_str, body_as_single_line)

    for_each_macro_def( macro_defs_file_path, handle_single_macro_def )
    return macros


formatter = Formatter()

def path_to_filename(path_to_js_needing_processing):
    return path_to_js_needing_processing[len(ST_ROOT + "/out/"):]

def run_macro_expansion(path_to_macro_defs, path_to_js_needing_processing, outfile_path, ignore_HAS_BEEN_PROCESSED_MARKER, key):
    starttime = perfcounter()
    
    # Use readlines() instead of read() has very insignificant performance cost, at least on my SSD
    # It's also useful to have the lines.
    lines = maybe_readlines_and_maybe_modify_first(
        path_to_js_needing_processing,
        HAS_BEEN_PROCESSED_MARKER__DEV,
        ignore_HAS_BEEN_PROCESSED_MARKER,
        key )
    if lines is None:
        return

    # print("[MCM] Read {} js lines.".format(len(lines)))
    # print("[MCM] File: " + path_to_filename(path_to_js_needing_processing) + "; read {} js lines in {} ms.".format(len(lines), round(1000*(perfcounter() - starttime))))

    # re that looks for //, /*, a macro name, or "function" on a single line
    def make_main_expansion_re( macronames ):
        macronames_with_paren = list(map(lambda x: x + r"\(", macronames))
        macroapp = "(" + "|".join(macronames_with_paren) + ")"
        #macroapp_with_nonword_prefix = "({}){}".format(NON_WORD_CHAR_OR_START_OF_STRING, macroapp)
        macroapp_with_nonword_prefix = "({}){}".format(RE_FOR_STUFF_BEFORE_MACRO_NAME, macroapp)

        comment_or_macroapp = "(?://)|(?:/\*)|(?:"+macroapp_with_nonword_prefix+")"
        # fn_defn_or_comment_or_macroapp = r"(?:(?:^|"+NON_WORD_CHAR_OR_START_OF_STRING+")function\s)|" + comment_or_macroapp  # matched too much
        fn_defn_or_comment_or_macroapp = r"(?:^function\s)|" + comment_or_macroapp
        return re.compile(fn_defn_or_comment_or_macroapp)

    line_num = 0
    num_matches = 0
    line_ind = 0

    outfile = open(outfile_path, 'w')
    def output_unchanged( s ):
        outfile.write(s)
        return line_ind + len(s)

    # start_macro_processing = perfcounter()
    macros = parse_macro_defs_file_to_substitution_objects(path_to_macro_defs)
    macronames = list(macros.keys())
    main_re = make_main_expansion_re(macronames)

    # print("[MCM] {} ms processing macro defs".format(round(1000*(perfcounter() - starttime))))

    # NTS: I gave it a a good try at making "for line in file" work with inserting console log.
    # Not worth trying any more. See ABOUT PERFORMANCE.txt
    if INSERT_CONSOLE_LOG_OF_BUILD_TIME:
        last_line_num_to_process = find_spot_for_console_msg(lines)
        if not last_line_num_to_process:
            last_line_num_to_process = len(lines) - 1    
    else:
        last_line_num_to_process = len(lines) - 1

    # print("last_line_num_to_process: ", last_line_num_to_process )
    # file_str = "".join(lines) # concatenation of lines

    in_multiline_comment = False
    while line_num <= last_line_num_to_process:

        while True:
            line = lines[line_num]

            if in_multiline_comment:
                match = END_BLOCK_COMMENT_RE.search(line, line_ind)
                if match: # */ found, with the / at index k:
                    # print("{} - end block comment. line_ind: {}. match.start()+1: {}. match.end()+1: {}, match.start(0)+1: {}. line[:-1]:\n{}\nmatch.group(0):\n{}".format(line_num+1,line_ind+1, match.start()+1, match.end()+1, match.start(0)+1, line[:-1], match.group(0)))
                    k = match.end()
                    line_ind = output_unchanged(line[line_ind:k]) # was k+1, which was wrong!
                    in_multiline_comment = False
                    continue # redundant
                else:
                    line_num += 1
                    output_unchanged(line[line_ind:])
                    line_ind = 0
                    break
            else:
                if line_ind > 0:
                    match = main_re.search(line, line_ind)
                else:
                    match = main_re.search(line)
                # line[line_ind:] is the remainder of the line
                if not match:
                    line_num += 1
                    output_unchanged(line[line_ind:])
                    line_ind = 0
                    break
                elif match.group(0) == "//":  # // found
                    line_num += 1
                    output_unchanged(line[line_ind:])
                    line_ind = 0
                    break
                elif match.group(0) == "/*": # /* found
                    # print("{} - start block comment. line_ind: {}. match.start()+1: {}. match.end()+1: {}, match.start(0)+1: {}. line[:-1]:\n{}\nmatch.group(0):\n{}".format(line_num+1,line_ind+1, match.start()+1, match.end()+1, match.start(0)+1, line[:-1], match.group(0)))
                    in_multiline_comment = True
                    line_ind = output_unchanged(line[line_ind: match.end(0)])
                    continue
                elif (line.strip().startswith("function")) or ("function " in match.group(0)):  # it's a function definition, perhaps of one of the macros, so skip this line
                    output_unchanged(line[line_ind:])
                    line_num += 1
                    line_ind = 0
                    break
                else: # macro name found
                    start_match_line_ind = match.start()
                    left_paren_ind = match.end() - 1
                    char_before_macro_or_empty, macroname_with_paren = match.groups()
                    if len(char_before_macro_or_empty) == 1:
                        line_ind = output_unchanged(line[line_ind:start_match_line_ind + 1])
                    else:
                        line_ind = output_unchanged(line[line_ind:start_match_line_ind])
                    macroname = macroname_with_paren[:-1]

                    in_chunk = OpenChunk(lines, line_num, left_paren_ind+1)
                    args_chunk = find_next_toplevel(in_chunk, ')')

                    args_chunk.stop_line_stop_ind -= 1  # now last char is the char before the ')'

                    list_of_arg_chunks = split_by_top_level_commas(args_chunk)

                    # OPT: don't need to form this list (really?)
                    args_list = list(map(lambda x: x.asSingleLine(), list_of_arg_chunks))

                    replacement_text = macros[macroname].simult_subst(args_list)

                    args_chunk.stop_line_stop_ind += 1 # now last char is the char after the ')'

                    if (args_chunk.stop_line_num - line_num) != 0:
                        WarningMsg("WARNING: macro application at line {} spans multiple lines. Line numbers could be affected.".format(line_num), args_chunk.stop_line_num - line_num + 1, len(args_list))
                        # replacement_text += "\n"*(nextline_num - line_num)
                        # print(".....", len(args_list), nextline_num+1, nextline_ind_of_right_paren+1, args_list)
                        # print(replacement_text)
                        # print(line[line_ind:])

                    num_matches += 1

                    outfile.write(replacement_text)
                    line_num = args_chunk.stop_line_num  # this will often be a noop, namely when the macro and its args are on the same line
                    line_ind = args_chunk.stop_line_stop_ind + 1
                    continue # redundant


    curtime = datetime.datetime.now().strftime("%I:%M:%S")
    if INSERT_CONSOLE_LOG_OF_BUILD_TIME: #and ("structure-together-main" in path_to_js_needing_processing):
        timestamp_print_command = "if(window.structure_together.dev_mode) {{ console.log('[{}] Build of {}'); }}\n".format(path_to_filename(path_to_js_needing_processing), curtime);
        outfile.write(timestamp_print_command);

    for line in lines[last_line_num_to_process + 1: len(lines)]:
        outfile.write(line)

    outfile.close()

    print("[MCM] {time} ms, replaced js file with macro-expanded code, {num} expansions\n".format(time=round(1000*(perfcounter() - starttime)), num=num_matches))


# e.g. if arg1 is a param that, in a macro occurrence, gets set to the value (in python) "x != 'a'",
# then svar(arg1) is an implicit param that, in the same macro occurrence, gets set to the value (in python)
# "x != \'a\'".
def svar(x):
    return "%" + x + "%"


if __name__ == '__main__':
    # NOTE: the last argument is always "1" for some reason to do with fswatch and xargs, and means nothing, so it will be ignored.
    # Also note: sys.argv[0] is the entire string of arguments
    # those two notes are why there's a descrepency between the length of sys.argv and the args used
    if len(sys.argv) == 5:
        run_macro_expansion(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 6:
        run_macro_expansion(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])


