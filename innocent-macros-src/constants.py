import re


USING_EXTERNAL_MODULES = True # this is a Typescript thing

DEBUGGING = True

# used by common.py
DEB_PRINT_ON = True
# used in expand_macros.py
VERBOSE_DEFAULT = True

HAS_BEEN_PROCESSED_MARKER__PRODUCTION = "// [IM] MACROS DELETED"
HAS_BEEN_PROCESSED_MARKER__DEV = "// [IM] MACROS EXPANDED"
INSERT_CONSOLE_LOG_OF_BUILD_TIME = True

NON_WORD_CHAR = "[^a-zA-Z0-9_$.]"

if USING_EXTERNAL_MODULES:
    RE_FOR_STUFF_BEFORE_MACRO_NAME = "".join([
        '(?:',
        '^', '|',
        '[^a-zA-Z0-9_$.]', '|', # macroFunctionName
        '(?:[a-zA-Z0-9_$]+\.)', # moduleName.macroFunctionName
        ')'
    ])
else:
    RE_FOR_STUFF_BEFORE_MACRO_NAME = NON_WORD_CHAR_OR_START_OF_STRING

END_BLOCK_COMMENT_RE = re.compile(r"\*/")


SINGLELINE_MACRO_DEF_RE = re.compile("".join([
    r"^\s*(?:export)?\s*function ",
    r"([^\s,(<>]+)",  # function name (i.e. macro name)
    r"(?:<[^(]+>)?",  # type var stuff
    r"\s*\(([^)]*)\)",  # function parameters
    r"\s*{\s*",
    r"(.+[^\s])",  # function body
    r"\s*}\s*$"
]))

# NTS the opening { must be on the same line as "function"
# NTS CANNOT match a single-line function, so try stuff must try SINGLELINE_MACRO_DEF_RE first.
FIRST_LINE_OF_MULTILINE_MACRO_DEF_RE = re.compile("".join([
    r"^\s*(?:export)?\s*function ",
    r"([^\s,(<>]+)",  # function name (i.e. macro name)
    r"(?:<[^(+]>)?",  # type var stuff
    r"\s*\(([^)]*)\)",  # function parameters
    r"(\s*:\s*[^\s{]+)?", # optional return type
    r"\s*{\s*$"  # opening {
]))
