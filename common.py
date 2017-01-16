import time, re
# from copy import copy
from constants import DEB_PRINT_ON, ST_ROOT
# from constants import VERBOSE_DEFAULT
from constants import FIRST_LINE_OF_MULTILINE_IDENTITY_FN_DEF_RE, FIRST_LINE_OF_MULTILINE_MACRO_DEF_RE
from constants import NON_WORD_CHAR, SINGLELINE_MACRO_DEF_RE



brackets_open_to_closed = {'(':')', '[':']', '{':'}'}
bracket_names = {'(':'parenthesis', '[':'square bracket', '{':'curly bracket'}

def path_to_filename(path_to_js_needing_processing):
    return path_to_js_needing_processing[len(ST_ROOT + "/out/"):]

def debprint(*args):
    if DEB_PRINT_ON:
        print(args)

# def some(lst):
#     for x in lst:
#         if x:
#             return True
#     return False

def perfcounter():
    # pydocs say this is preferred if you're using python 3.x:
    # return time.perfcounter()
    return time.clock()


#
# def strOccurrenceisTokenOccurrence(token, text, start):
#     """
#     PRE: text[start: start + len(token)] == token
#     :param token:
#     :param text:
#     :param start:
#     :return: true iff text[start: start + len(token)] is not within a larger token
#     """
#     end = start + len(token)
#     if start == 0 or re.search(NON_WORD_CHAR, text[start-1]):
#         return end == len(text) - 1 or re.search(NON_WORD_CHAR, text[end+1])
#     else:
#         return False

def couldBeToken(start, stop, text):
    """
    :param start:
    :param stop:
    :param text:
    :return:
    """
    if start == 0 or re.search(NON_WORD_CHAR, text[start-1]):
        return stop == len(text) - 1 or re.search(NON_WORD_CHAR, text[stop+1])
    else:
        return False


def updateInStrLit(in_str_lit, i, text):
    """
    :param in_str_lit: dict {"'":boolean, '"':boolean, '`':boolean} that is all false if i == 0, and otherwise
     tells whether text[i-1] is within a string literal or the corresponding type.
    :param i:
    :param text:
    :return:
    """
    a = text[i]

    if a == "'":
        # if the ' isn't escaped AND we're not inside a " or ` quoted string.
        if text[min(i - 1, 0)] != "\\" and not in_str_lit['"'] and not in_str_lit["`"]:
            in_str_lit["'"] = not in_str_lit["'"]
    elif a == '"':
        # if the " isn't escaped AND we're not inside a ' or ` quoted string.
        if text[min(i - 1, 0)] != "\\" and not in_str_lit["'"] and not in_str_lit["`"]:
            in_str_lit['"'] = not in_str_lit['"']
    elif a == '`':
        # if the ` isn't escaped AND we're not inside a ' or " quoted string.
        if text[min(i - 1, 0)] != "\\" and not in_str_lit["'"] and not in_str_lit['"']:
            in_str_lit['`'] = not in_str_lit['`']

def inStrLiteral(in_str_lit):
    return in_str_lit['"'] or in_str_lit["'"] or in_str_lit["`"]

def updateOpenBracketCnts(open_bracket_cnt, i, text):
    """
    PRE: text[i] is not within a string literal
    :param open_bracket_cnt:
    :param i:
    :param text:
    """
    a = text[i]
    if a == "(":
        open_bracket_cnt["("] += 1
    elif a == "{":
        open_bracket_cnt["{"] += 1
    elif a == "[":
        open_bracket_cnt["["] += 1
    elif a == ")":
        open_bracket_cnt["("] -= 1
    elif a == "}":
        open_bracket_cnt["{"] -= 1
    elif a == "]":
        open_bracket_cnt["["] -= 1

def bracketsBalanced(open_bracket_cnt):
    return open_bracket_cnt["("] == open_bracket_cnt["{"] == open_bracket_cnt["["] == 0

def unmatchedCloseBracket(open_bracket_cnt):
    return open_bracket_cnt["("] < 0 or open_bracket_cnt["{"] < 0 or open_bracket_cnt["["] < 0

"""
not yet used
class Line(object):
    def __init__(self,
                 lineslst,
                 line_num,
                 start_ind = None,
                 stop_ind = None
                 ):
        self.lineslst = lineslst
        self.line_num = line_num
        self.start_ind = start_ind or 0
        self.stop_ind = stop_ind or len(lines[line_num]) - 1
"""

def escapeQuotes(x):
    return x.replace("'","\\'").replace('"','\\"').replace("`","\\`")

class Paragraph(object):
    """
    stop_line_stop_ind is INCLUSIVE
    stop_line_stop_ind is None iff stop_line_num is None
    A Paragraph is "open" iff stop_line_num == None. It's "closed" otherwise.

    """

    def __init__(self,
                 lines,
                 start_line_num,
                 start_line_start_ind,
                 stop_line_num,
                 stop_line_stop_ind
                 ):
        self.lines = lines
        self.start_line_num = start_line_num
        self.start_line_start_ind = start_line_start_ind

        self.stop_line_num = stop_line_num
        self.stop_line_stop_ind = stop_line_stop_ind

        assert( stop_line_num is None or stop_line_stop_ind is not None )
        assert( stop_line_num is not None or stop_line_stop_ind is None )


    def delete_last_char(self):
        if self.stop_line_stop_ind > 0:
            self.stop_line_stop_ind -= 1
        else:
            assert self.stop_line_num >= 1, "Empty pararaph? " + repr(self)
            self.stop_line_num -= 1
            self.stop_line_stop_ind = len(
                self.lines[self.stop_line_num]) - 1  # so will this always be the newline char?

    def asListOfLineStrings(self):
        if self.stop_line_num is None or self.stop_line_stop_ind is None:
            raise Exception("Method undefined on unclosed paragraph")
        if self.start_line_num < self.stop_line_num:
            rv = [self.lines[self.start_line_num][self.start_line_start_ind:]]
            rv.extend(self.lines[self.start_line_num + 1: self.stop_line_num])
            rv.append(self.lines[self.stop_line_num][:self.stop_line_stop_ind + 1])
            return rv
        else:
            return [self.lines[self.start_line_num][self.start_line_start_ind:self.stop_line_stop_ind + 1]]

    @staticmethod
    def fromSingleLine(s):
        return Paragraph([s], 0, 0, 0, len(s) - 1)

    def asSingleLine(self):
        if self.stop_line_num is None or self.stop_line_stop_ind is None:
            raise Exception("Method undefined on open paragraph")
        return "".join(self.asListOfLineStrings())

    def numbersTuple(self):
        return self.start_line_num, self.start_line_start_ind, self.stop_line_num, self.stop_line_stop_ind

    def __repr__(self):
        return "Paragraph({},{},{},{},{})".format(self.lines, self.start_line_num, self.start_line_start_ind,
                                                  self.stop_line_num, self.stop_line_stop_ind)

class OpenParagraph(Paragraph):
    def __init__(self,
                 lines,
                 start_line_num,
                 start_line_start_ind):
        Paragraph.__init__(self, lines, start_line_num, start_line_start_ind, None, None)

def find_next_toplevel_in_str(s, start, char_to_find):
    # print(start)
    # print(s[start:start+300])
    par = OpenParagraph([s], 0, start)
    res = find_next_toplevel(par, char_to_find)
    if not res:
        return res
    # print(res.stop_line_stop_ind)
    return res.stop_line_stop_ind    


def find_next_toplevel(par, char_to_find):
    r"""
    @:param par : Paragraph
    @:param char_to_find : character
    @returns None if none found, or else a Paragraph with
    lines = par.lines
    start_line_num = par.start_line_num
    start_line_ind = par.start_line_ind
    stop_line_num = first line in par containing a top-level char_to_find
    stop_line_stop_ind = index in stop_line_num of the top-level char_to_find

    >>> aline = ['functioncall(0,1,2)\n']
    >>> find_next_toplevel(OpenParagraph(aline, 0, 13), ')')
    Paragraph(['functioncall(0,1,2)\n'],0,13,0,18)
    >>> [find_next_toplevel(OpenParagraph(aline, 0, 12), ')')]
    [None]

    >>> lines = ['line 1\n', '\n', 'line 2(\n', 'a, b, \n', 'c\n', ')\n', 'a\n']
    >>> find_next_toplevel(OpenParagraph(lines, 0, 0), 'a')
    Paragraph(['line 1\n', '\n', 'line 2(\n', 'a, b, \n', 'c\n', ')\n', 'a\n'],0,0,6,0)
    >>> lines2 = [ '"Problem with prop " + p + ", allowed_flatprops(p) is " + allowed_flatprops[p] + ", nodetype is " + node.nodetype']
    >>> find_next_toplevel(OpenParagraph(lines2, 0, 0), ',')
    """
    rv = Paragraph(par.lines, par.start_line_num, par.start_line_start_ind, None, None)

    line_ind = par.start_line_start_ind

    # Number of open Round, Square, and Curly brackets, respectively, in the part of lines scanned so far
    # i.e. up to lines[line_num][line_ind]
    # exception if any are ever negative.
    bracket_cnts = {'(':0, '[':0, '{':0}

    # Whether lines[line_num][line_ind] is inside a Single/Double/Back quoted string
    in_str_lit = {"'":False, '"':False, '`':False}

    found = False
    line_num = par.start_line_num

    stop_line_num = par.stop_line_num if (par.stop_line_num is not None) else len(par.lines) - 1

    assert stop_line_num <= len(par.lines) - 1, repr(par)
    while not found and line_num <= stop_line_num:

        line = par.lines[line_num]

        if par.stop_line_stop_ind is not None and line_num == par.stop_line_num:
            stop_line_ind = par.stop_line_stop_ind
        else:
            stop_line_ind = len(line) - 1

        while True:
            a = line[line_ind]

            if not inStrLiteral(in_str_lit):

                if a == "/" and line_ind < len(line) - 1 and line[line_ind + 1] == "/":
                    # this is a comment line. ignore it
                    break

                # possibly the character occurrence we're looking for, if the context is right.
                if a == char_to_find:
                    # check if brackets are balanced and we're not inside a string literal, in which case we're done.
                    if bracketsBalanced(bracket_cnts) and not inStrLiteral(in_str_lit):
                        # debprint("found on line {} (1-based) at ind {} (1-based)".format(line_num + 1, line_ind + 1))
                        # next two lines cause both loops to exit
                        found = True
                        break

                updateOpenBracketCnts(bracket_cnts, line_ind, line)

            # BAD --> if we're at the end of the line, i.e. at a line ending character, then break this loop,
            # which continues the outer loop. this isn't necessary, but might as well since
            # all the remaining if-statement conditions will be false.
            # Bad because the last character need not be an endline.
            # later --> ...wait really?
            # if line_ind == len(line) - 1:
            # 	debprint(a, " is a line ending?")
            # 	break
            updateInStrLit(in_str_lit, line_ind, line)


            if unmatchedCloseBracket(bracket_cnts):
                # msg = "[MCM] Unmatched close-paren/bracket at line {} (1-based)?\n".format(start_line_num + line_endings_passed + 1)
                msg = "[MCM] There seems to be an unmatched close-paren/bracket in line {}[1-based], found while looking for the next '{}'.\n".format(
                    line_num + 1, char_to_find)

                for b in bracket_cnts.keys():
                    if bracket_cnts[b] < 0:  msg += "Unmatched closed " + bracket_names[b] + "\n"

                for b in bracket_cnts.keys():
                    msg += "Also, we'd counted {} open {} brackets when this exception happened.\n".format(bracket_cnts[b], b)

                raise Exception(msg)

            if line_ind == stop_line_ind:
                break
            line_ind += 1

        if found or line_num == stop_line_num:
            break

        line_num += 1
        line_ind = 0

    # next checks aren't necessary if macros file has been parsed by tsc:
    if not bracketsBalanced(bracket_cnts) or inStrLiteral(in_str_lit):
        print(repr(par))
        # msg = "[MCM] Unclosed paren/bracket or quote at line {} (1-based)?\n".format(start_line_num + line_endings_passed + 1)
        msg = "[MCM] Unclosed paren/bracket or quote at line {} (1-based)?\n".format(line_num + 1)
        for b in bracket_cnts.keys():
            if bracket_cnts[b] < 0:  msg += "Unclosed " + bracket_names[b] + "\n"
        for q in in_str_lit.keys():
            if in_str_lit[q] < 0:  msg += "Unclosed " + q + "\n"
        raise Exception(msg)

    if not found:
        return None

    rv.stop_line_num = line_num
    rv.stop_line_stop_ind = line_ind

    return rv







def split_by_top_level_commas(bigger_par):
    """
    Takes a CLOSED paragraph @bigger_par of a valid function call,
    NO -> optionally beginning and ending with the opening '(' and closing ')'
    Returns a list of paragraphs for the individual arguments, each of which may span multiple lines.
    """
    r"""
    >>> lines = ["debugtest(this.node_class_names.forEach(function (nodetype) {\n", "	dassert(_this.strict_subtype_reln.has(nodetype), nodetype);\n", "	dassert(_this.strict_supertype_reln.has(nodetype), nodetype);\n", "}));"]
    >>> par = Paragraph(lines, 0, 10, 3, 1)
    >>> rv = split_by_top_level_commas(par)
    >>> map( lambda x: x.numbersTuple(), rv)
    [(0, 10, 3, 1)]
    >>> lines2 = ["fn(10 , 20,\n", "30,\n", "40,50\n", "   )\n"]
    >>> par2 = Paragraph(lines2, 0, 3, 3, 2)
    >>> rv2 = split_by_top_level_commas(par2)
    >>> map( lambda x: x.numbersTuple(), rv2)
    [(0, 3, 0, 5), (0, 7, 0, 9), (0, 11, 1, 1), (1, 3, 2, 1), (2, 3, 3, 2)]
    >>> lines3 = ["debugtest(this.node_class_names.forEach(function (nodetype) {\n","                dassert(_this.strict_subtype_reln.has(nodetype), nodetype);\n","                dassert(_this.strict_supertype_reln.has(nodetype), nodetype);\n","            }));\n"]
    >>> par3 = Paragraph(lines3, 0, 10, 3, 13)
    >>> rv3 = split_by_top_level_commas(par3)
    >>> map( lambda x: x.numbersTuple(), rv3)
    [(0, 10, 3, 13)]
    >>> line = ['dassert(allowed_flatprops[p] === StringPropType.immutstring || allowed_flatprops[p] === StringPropType.stringselect, "Problem with prop " + p + ", allowed_flatprops(p) is " + allowed_flatprops[p] + ", nodetype is " + node.nodetype);' ]
    >>> par4 = Paragraph(line, 0, 9, 0, 212)
    >>> rv4 = split_by_top_level_commas(par4)
    >>> map( lambda x: x.numbersTuple(), rv4)
    3
    """
    # OLD:
    # assert bigger_par.lines[bigger_par.start_line_num][bigger_par.start_line_start_ind] == "("
    # assert bigger_par.lines[bigger_par.stop_line_num][bigger_par.stop_line_stop_ind] == ")"

    # idea: use find_next_toplevel repeatedly until end of par
    arg_pars = []
    remaining_args_par = Paragraph(
        bigger_par.lines,
        bigger_par.start_line_num,
        bigger_par.start_line_start_ind,
        bigger_par.stop_line_num,
        bigger_par.stop_line_stop_ind
    )

    while True:
        next_arg_par = find_next_toplevel(remaining_args_par, ",")
        if next_arg_par is not None:
            # for next iteration of loop:
            remaining_args_par.start_line_num = next_arg_par.stop_line_num
            remaining_args_par.start_line_start_ind = next_arg_par.stop_line_stop_ind + 1  # start just after the ','
            next_arg_par.delete_last_char() #  adjust to not include the ','
            arg_pars.append(next_arg_par)
        else:
            # then we're done, which means the final arg is just remaining_args_par
            arg_pars.append(remaining_args_par)
            break
    return arg_pars



def for_each_macro_def(macro_defs_file_path, f):
    """
    f is a function that takes a tripple (fnname: string, params_str: string, body_as_single_line: string) and returns nothing.
    It will be called on each such tripple parsed from the file at path macro_defs_file_path.
    """
    macro_defs_file = open(macro_defs_file_path, 'r')
    macro_defs_file_lines = macro_defs_file.readlines()
    macro_defs_file.close()

    i = 0
    file_ind = 0
    while i < len(macro_defs_file_lines):
        line = macro_defs_file_lines[i]
        if line.startswith("//STOP"):
            print("[IM] Found '//STOP' in macro defs file")
            return
        # match = SINGLELINE_NONVOID_MACRO_DEF_RE.match(line)
        # if match:
        # 	fnname, params_str, body  = match.groups()
        # 	i += 1
        # 	f(fnname, params_str, body)
        # 	continue
        if (line.startswith("import") or line.startswith("const") or line.startswith("window") or 
            line.startswith("declare") or line.startswith("type") ):
            i += 1
            continue

        match = SINGLELINE_MACRO_DEF_RE.match(line)
        if match:
            fnname, params_str, body = match.groups()
            i += 1
            f(fnname, params_str, body)
            continue

        match = FIRST_LINE_OF_MULTILINE_MACRO_DEF_RE.match(line)
        if match:
            fnname, params_str, opt_returntype = match.groups()

            body_par = find_next_toplevel(OpenParagraph(macro_defs_file_lines, i + 1, 0), "}")

            # remove any single-line comments, and exclude the line containing the final }
            body_lines = filter(lambda x: not x.strip().startswith("//"),
                                body_par.lines[body_par.start_line_num:body_par.stop_line_num])

            # remove the endlines and extra whitespace, then join as single string
            body_str = "".join(map(lambda s: s.strip(), body_lines))

            if opt_returntype:
                assert( body_str.startswith("return ") ) 
                body_str = body_str[7:]
                if body_str[-1] == ";":
                    body_str = body_str[:-1]

                print("\nFOUND NON-VOID NON-IDENTITY MACRO. body_str is\n" + body_str + "\n")

            # print(body_str)
            i = body_par.stop_line_num + 1

            
            f(fnname, params_str, body_str)
            continue    

        else:
            stripped = line.strip()
            assert stripped == "" or stripped.startswith("//"), "\nThe line \n\t" + line + \
                                                                "is not recognized as an empty line, a single-line comment, or as part of a macro definition.\n" + \
                                                                "Nothing else is allowed (including /* */ comments).\n" + \
                                                                "Note that the { following the parameters of a macro definition must be on the same line as \"function\"."
            i += 1
            continue





def maybe_readlines_and_maybe_modify_first(path, has_been_processed_marker, ignore_HAS_BEEN_PROCESSED_MARKER, key):
    # print("in maybe_readlines_and_maybe_modify_first")
    f = open(path, "r")
    firstline = f.readline()

    if has_been_processed_marker in firstline:
        if ignore_HAS_BEEN_PROCESSED_MARKER:
            lines = [firstline]  # so we don't duplicate the has-been-processed marker
        else:
            print("\t[IM] Found '{}' in source for build {}. Will stop.".format(has_been_processed_marker, key))
            f.close()
            return None
    else:
        lines = [firstline[:-1] + has_been_processed_marker + "\n"]

    lines.extend(f.readlines())
    f.close()
    return lines

def maybe_readfile_as_string_and_insert_marker(path, has_been_processed_marker, ignore_HAS_BEEN_PROCESSED_MARKER, key):
    # print("in maybe_readlines_and_maybe_modify_first")
    f = open(path, "r")
    filestr = f.read()
    f.close()
    
    # look in the first 100 characters only
    if has_been_processed_marker in filestr[:100]: 
        if not ignore_HAS_BEEN_PROCESSED_MARKER:
            print("\t[IM] Found '{}' in source for build {}. Will stop.".format(has_been_processed_marker, key))
            f.close()
            return None            
    else:
        filestr = has_been_processed_marker + "\n" + filestr        

    return filestr

def find_spot_for_console_msg(lines):
    """
    look backwards through lines to find index k of the file's last line that doesn't start with //
    # return k
    """
    i = len(lines) - 1

    while i >= 0:
        if lines[i].startswith("//"):
            i -= 1
        else:
            return i


if __name__ == "__main__":
    import doctest

    doctest.testmod()
