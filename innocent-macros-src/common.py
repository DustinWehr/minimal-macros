import time, re
from typing import Callable, List, Dict, Union

from constants import DEB_PRINT_ON, FIRST_LINE_OF_MULTILINE_MACRO_DEF_RE, NON_WORD_CHAR, SINGLELINE_MACRO_DEF_RE

brackets_open_to_closed = {'(':')', '[':']', '{':'}'}
bracket_names = {'(':'parenthesis', '[':'square bracket', '{':'curly bracket'}


def debprint(*args):
    if DEB_PRINT_ON:
        print(args)

def perfcounter():    
    return time.clock()
    # pydocs say this is preferred if you're using python 3.x:
    # return time.perfcounter()


def couldBeToken(start:int, stop:int, text:str) -> bool:
    """
    Pre: 0 <= start <= stop <= len(text) - 1
    Return true iff
        start == 0 or text[start-1] is a non-word character, and
        stop == len(text)-1 or text[stop+1] is a non-word character

    This should be equivalent to some search using re.search("\b\w+\b" ...
    """
    if start == 0 or re.search(NON_WORD_CHAR, text[start-1]):
        return stop == len(text) - 1 or re.search(NON_WORD_CHAR, text[stop+1])
    else:
        return False


def updateInStrLit(in_str_lit:Dict[str,bool], i:int, text:str) -> None:
    """
    :param in_str_lit: dict {"'":boolean, '"':boolean, '`':boolean} that is all false if i == 0, and otherwise
     tells whether text[i-1] is within a string literal of the corresponding type.
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

def inStrLiteral(in_str_lit:Dict[str,bool]) -> bool:
    return in_str_lit['"'] or in_str_lit["'"] or in_str_lit["`"]

def updateOpenBracketCnts(open_bracket_cnt:Dict[str,int], i:int, text:str) -> None:
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

def bracketsBalanced(open_bracket_cnt:Dict[str,int]) -> bool:
    return open_bracket_cnt["("] == open_bracket_cnt["{"] == open_bracket_cnt["["] == 0

def unmatchedCloseBracket(open_bracket_cnt:Dict[str,int]) -> bool:
    return open_bracket_cnt["("] < 0 or open_bracket_cnt["{"] < 0 or open_bracket_cnt["["] < 0

def escapeQuotes(x):
    # TODO: this is probably not a fully general solution
    return x.replace("'","\\'").replace('"','\\"').replace("`","\\`")

class Chunk(object):
    """
    stop_line_stop_ind is INCLUSIVE
    stop_line_stop_ind is None iff stop_line_num is None
    A Chunk is "open" iff stop_line_num == None. It's "closed" otherwise.
    """

    def __init__(self,
                 lines:List[str],
                 start_line_num:int,
                 start_line_start_ind:int,
                 stop_line_num:int,
                 stop_line_stop_ind:int
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
                self.lines[self.stop_line_num]) - 1  # this is not necessarily the newline char (i think)

    def asListOfLineStrings(self):
        if self.stop_line_num is None or self.stop_line_stop_ind is None:
            raise Exception("Method undefined on open chunk")
        if self.start_line_num < self.stop_line_num:
            rv = [self.lines[self.start_line_num][self.start_line_start_ind:]]
            rv.extend(self.lines[self.start_line_num + 1: self.stop_line_num])
            rv.append(self.lines[self.stop_line_num][:self.stop_line_stop_ind + 1])
            return rv
        else:
            return [self.lines[self.start_line_num][self.start_line_start_ind:self.stop_line_stop_ind + 1]]

    @staticmethod
    def fromSingleLine(s:str) -> 'Chunk':
        return Chunk([s], 0, 0, 0, len(s) - 1)

    def asSingleLine(self):
        if self.stop_line_num is None or self.stop_line_stop_ind is None:
            raise Exception("Method undefined on open chunk")
        return "".join(self.asListOfLineStrings())

    def numbersTuple(self):
        return self.start_line_num, self.start_line_start_ind, self.stop_line_num, self.stop_line_stop_ind

    def __repr__(self):
        return "Chunk({},{},{},{},{})".format(self.lines, self.start_line_num, self.start_line_start_ind,
                                                  self.stop_line_num, self.stop_line_stop_ind)

class ClosedChunk(Chunk):
    def __init__(self,
                 lines,
                 start_line_num,
                 start_line_start_ind,
                 stop_line_num:int,
                 stop_line_stop_ind:int):
        assert(stop_line_num is not None and stop_line_stop_ind is not None)
        Chunk.__init__(self, lines, start_line_num, start_line_start_ind, stop_line_num, stop_line_stop_ind)

class OpenChunk(Chunk):
    def __init__(self,
                 lines,
                 start_line_num,
                 start_line_start_ind):
        Chunk.__init__(self, lines, start_line_num, start_line_start_ind, None, None)

def find_next_toplevel_in_str(s:str, start:int, char_to_find:str) -> int:
    chunk = OpenChunk([s], 0, start)
    res = find_next_toplevel(chunk, char_to_find)
    if not res:
        return res
    return res.stop_line_stop_ind


def find_next_toplevel(chunk:Chunk, char_to_find:str) -> Union[ClosedChunk,None]:
    """
    @:param chunk : Chunk
    @:param char_to_find : character
    @returns None if none found, or else a ClosedChunk with
    lines = chunk.lines
    start_line_num = chunk.start_line_num
    start_line_ind = chunk.start_line_ind
    stop_line_num = first line in chunk containing a top-level char_to_find
    stop_line_stop_ind = index in stop_line_num of the top-level char_to_find

    >>> aline = ['functioncall(0,1,2)\n']
    >>> find_next_toplevel(OpenChunk(aline, 0, 13), ')')
    Chunk(['functioncall(0,1,2)\n'],0,13,0,18)
    >>> [find_next_toplevel(OpenChunk(aline, 0, 12), ')')]
    [None]

    >>> lines = ['line 1\n', '\n', 'line 2(\n', 'a, b, \n', 'c\n', ')\n', 'a\n']
    >>> find_next_toplevel(OpenChunk(lines, 0, 0), 'a')
    Chunk(['line 1\n', '\n', 'line 2(\n', 'a, b, \n', 'c\n', ')\n', 'a\n'],0,0,6,0)
    >>> lines2 = [ '"Problem with prop " + p + ", allowed_flatprops(p) is " + allowed_flatprops[p] + ", nodetype is " + node.nodetype']
    >>> find_next_toplevel(OpenChunk(lines2, 0, 0), ',')
    """
    rv = Chunk(chunk.lines, chunk.start_line_num, chunk.start_line_start_ind, None, None)

    line_ind = chunk.start_line_start_ind

    # Number of open Round, Square, and Curly brackets, respectively, in the part of lines scanned so far
    # i.e. up to lines[line_num][line_ind]
    # exception if any are ever negative.
    bracket_cnts = {'(':0, '[':0, '{':0}

    # Whether lines[line_num][line_ind] is inside a Single/Double/Back quoted string
    in_str_lit = {"'":False, '"':False, '`':False}

    found = False
    line_num = chunk.start_line_num

    stop_line_num = chunk.stop_line_num if (chunk.stop_line_num is not None) else len(chunk.lines) - 1

    assert stop_line_num <= len(chunk.lines) - 1, repr(chunk)
    while not found and line_num <= stop_line_num:

        line = chunk.lines[line_num]

        if chunk.stop_line_stop_ind is not None and line_num == chunk.stop_line_num:
            stop_line_ind = chunk.stop_line_stop_ind
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
                        # next two lines cause both loops to exit
                        found = True
                        break

                updateOpenBracketCnts(bracket_cnts, line_ind, line)

            updateInStrLit(in_str_lit, line_ind, line)


            if unmatchedCloseBracket(bracket_cnts):
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
        print(repr(chunk))
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




def split_by_top_level_commas(bigger_chunk:ClosedChunk) -> List[ClosedChunk]:
    """
    Takes a CLOSED chunk @bigger_chunk of a valid function call in some source text,
    NO -> optionally beginning and ending with the opening '(' and closing ')'
    Returns a list of closed chunks for the individual arguments, each of which may span multiple lines.
    """
    r"""
    >>> lines = ["debugtest(this.node_class_names.forEach(function (nodetype) {\n", "	dassert(_this.strict_subtype_reln.has(nodetype), nodetype);\n", "	dassert(_this.strict_supertype_reln.has(nodetype), nodetype);\n", "}));"]
    >>> chunk = Chunk(lines, 0, 10, 3, 1)
    >>> rv = split_by_top_level_commas(chunk)
    >>> map( lambda x: x.numbersTuple(), rv)
    [(0, 10, 3, 1)]
    >>> lines2 = ["fn(10 , 20,\n", "30,\n", "40,50\n", "   )\n"]
    >>> chunk2 = Chunk(lines2, 0, 3, 3, 2)
    >>> rv2 = split_by_top_level_commas(chunk2)
    >>> map( lambda x: x.numbersTuple(), rv2)
    [(0, 3, 0, 5), (0, 7, 0, 9), (0, 11, 1, 1), (1, 3, 2, 1), (2, 3, 3, 2)]
    >>> lines3 = ["debugtest(this.node_class_names.forEach(function (nodetype) {\n","                dassert(_this.strict_subtype_reln.has(nodetype), nodetype);\n","                dassert(_this.strict_supertype_reln.has(nodetype), nodetype);\n","            }));\n"]
    >>> par3 = Chunk(lines3, 0, 10, 3, 13)
    >>> rv3 = split_by_top_level_commas(par3)
    >>> map( lambda x: x.numbersTuple(), rv3)
    [(0, 10, 3, 13)]
    >>> line = ['dassert(allowed_flatprops[p] === StringPropType.immutstring || allowed_flatprops[p] === StringPropType.stringselect, "Problem with prop " + p + ", allowed_flatprops(p) is " + allowed_flatprops[p] + ", nodetype is " + node.nodetype);' ]
    >>> par4 = Chunk(line, 0, 9, 0, 212)
    >>> rv4 = split_by_top_level_commas(par4)
    >>> map( lambda x: x.numbersTuple(), rv4)
    3
    """

    # idea: use find_next_toplevel repeatedly until end of chunk
    arg_chunks = []
    remaining_args_chunk = Chunk(
        bigger_chunk.lines,
        bigger_chunk.start_line_num,
        bigger_chunk.start_line_start_ind,
        bigger_chunk.stop_line_num,
        bigger_chunk.stop_line_stop_ind
    )

    while True:
        next_arg_chunk = find_next_toplevel(remaining_args_chunk, ",")
        if next_arg_chunk is not None:
            # for next iteration of loop:
            remaining_args_chunk.start_line_num = next_arg_chunk.stop_line_num
            remaining_args_chunk.start_line_start_ind = next_arg_chunk.stop_line_stop_ind + 1  # start just after the ','
            next_arg_chunk.delete_last_char() #  adjust to not include the ','
            arg_chunks.append(next_arg_chunk)
        else:
            # then we're done, which means the final arg is just remaining_args_chunk
            arg_chunks.append(remaining_args_chunk)
            break
    return arg_chunks



def for_each_macro_def(macro_defs_file_path:str, f:Callable[[str,str,str],None]):
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

            body_chunk = find_next_toplevel(OpenChunk(macro_defs_file_lines, i + 1, 0), "}")

            # remove any single-line comments, and exclude the line containing the final }
            body_lines = filter(lambda x: not x.strip().startswith("//"),
                                body_chunk.lines[body_chunk.start_line_num:body_chunk.stop_line_num])

            # remove the endlines and extra whitespace, then join as single string
            body_str = "".join(map(lambda s: s.strip(), body_lines))

            if opt_returntype:
                assert( body_str.startswith("return ") ) 
                body_str = body_str[7:]
                if body_str[-1] == ";":
                    body_str = body_str[:-1]

                print("\nFOUND NON-VOID NON-IDENTITY MACRO. body_str is\n" + body_str + "\n")

            i = body_chunk.stop_line_num + 1 

            
            f(fnname, params_str, body_str)
            continue    

        else:
            stripped = line.strip()
            assert stripped == "" or stripped.startswith("//"), "\nThe line \n\t" + line + \
                                                                "is not recognized as an empty line, a single-line comment, or as part of a macro definition.\n" + \
                                                                "Nothing else is allowed (including /* */ comments).\n" + \
                                                                "Note that the '{' following the parameters of a macro definition must be on the same line as \"function\"."
            i += 1
            continue


def maybe_readlines_and_maybe_modify_first(path:str, has_been_processed_marker:str, ignore_HAS_BEEN_PROCESSED_MARKER:bool, key:str):
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

def maybe_readfile_as_string_and_insert_marker(path:str, has_been_processed_marker:str, ignore_HAS_BEEN_PROCESSED_MARKER:bool, key:str):
    # print("in maybe_readfile_as_string_and_insert_marker")
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

def find_spot_for_console_msg(lines: List[str]) -> int:
    """
    Look backwards through lines to find index k of the file's last line that doesn't start with //
    This is an attempt to not interfere with other tools that place a "hot comment" at the end of the file.
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
