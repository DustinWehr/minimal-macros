import re


USING_EXTERNAL_MODULES = True # this is a Typescript thing
DEBUGGING = True

NON_WORD_CHAR = "[^a-zA-Z0-9_$.]"

if USING_EXTERNAL_MODULES:
    RE_FOR_STUFF_BEFORE_MACRO_NAME = "".join([
        '(?:',
        '^', '|',
        '[^a-zA-Z0-9_$.]', '|', # nonword character
        '(?:[a-zA-Z0-9_$]+\.)', # moduleName.  nested modules not yet supported
        ')'
    ])
else:
    RE_FOR_STUFF_BEFORE_MACRO_NAME = NON_WORD_CHAR_OR_START_OF_STRING

END_BLOCK_COMMENT_RE = re.compile(r"\*/")


SINGLELINE_MACRO_DEF_RE = re.compile("".join([
    r"^\s*(?:export)?\s*function ",
    r"([^\s,(<>]+)",  # function name (i.e. macro name)
    r"(?:<[^(]+>)?",  # type var stuff
    # r"\s*\(([^)]*)\)",  # function parameters. This is incompatible with function types in params, and also unnecessary
    r"\s*\((.*)\)",  # function parameters
    r"\s*{\s*",      # opening {
    r"(.+[^\s])",  # function body
    r"\s*}\s*$" # closing }
]))

# NTS the opening { must be on the same line as "function"
# NTS CANNOT match a single-line function, so try stuff must try SINGLELINE_MACRO_DEF_RE first.
FIRST_LINE_OF_MULTILINE_MACRO_DEF_RE = re.compile("".join([
    r"^\s*(?:export)?\s*function ",
    r"([^\s,(<>]+)",  # function name (i.e. macro name)
    r"(?:<[^(+]>)?",  # type var stuff
    # r"\s*\(([^)]*)\)",  # function parameters. This is incompatible with function types in params, and also unnecessary
    r"\s*\((.*)\)",  # function parameters
    # r"(\s*:\s*[^\s{]+)?", # optional return type # non-void macro functions no longer supported
    r"(\s*:\s*void)?", # optional 'void'
    r"\s*{\s*$"  # opening {
]))
