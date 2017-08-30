#! /usr/bin/env python3
import sys
sys.path.extend(["../src", "./src"])
import YOUR_PROJECT_SPECIFIC_MAIN_FILE_TO_MODIFY as script
import minimal_macros_api_with_watch as lib


print("""
This is a ghetto test. It "passes" if you see no errors and output similar to the following (but not identical, due to the run time reports):
I believe the numbers 763, 759, 699 are different because of dead code elimination by Google Closure Compiler.

[IM] No '-d' ('--delete') or '-e' ('--expand') arg given, so using your config object to determine which files to expand/delete macros in.
[IM] Processing build 'dev'
	[IM] Expanded 763 macro occurrences, 823 ms
[IM] Processing build 'scc'
	[IM] Deleted 759 macro occurrences, 234 ms
[IM] Processing build 'acc'
	[IM] Deleted 699 macro occurrences, 176 ms

TEST STARTING NOW
""")



lib.start_processing(script.config, [])

