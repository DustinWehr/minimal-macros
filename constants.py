import re

# used by innocent_macros_main.py:
# MACROS_PROJECT_ROOT = "/Users/dustin/Sites/LfP/StructureTogether/scripts/innocent-macros"
# EXPANSION_SCRIPT_NAME = "expand_macros.py"
# DELETION_SCRIPT_NAME = "delete_macros.py"

ST_ROOT = "/Users/dustin/Sites/LfP/StructureTogether"

TS_MACRO_DEFS_PATH = ST_ROOT + "/src/macros/dev-mode/dwmacros_multiline.ts"
SRC_WITH_MACRO_OCCURRENCES_TO_PROCESS = ST_ROOT + "/out/structure-together-main.webpack-entry-chunk.js"

# WITH_MACRO_OCCURRENCES_TO_PROCESS = [
#     "/out/structure-together-main.webpack-entry-chunk.js",
#     "/out/structure-together-core.webpack-entry-chunk.js",
#     "/out/structure-together-test.webpack-entry-chunk.js",
#     "/out/syncing-data.webpack-entry-chunk.js",
#     "/out/util.webpack-entry-chunk.js",
#     "/out/ifpd-language.webpack-entry-chunk.js"
# ]

# PATHS_WITH_MACRO_OCCURRENCES_TO_PROCESS = [ST_ROOT + x for x in WITH_MACRO_OCCURRENCES_TO_PROCESS]

USING_EXTERNAL_MODULES = True

DEBUGGING = True


# used by common.py
DEB_PRINT_ON = True
# used in expand_macros.py
VERBOSE_DEFAULT = True

HAS_BEEN_PROCESSED_MARKER__PRODUCTION = "// [MCM] MACROS DELETED"
HAS_BEEN_PROCESSED_MARKER__DEV = "// [MCM] MACROS EXPANDED"
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
