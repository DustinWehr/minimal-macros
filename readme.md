# Innocent Macros for TypeScript/JavaScript

**Please note: This project is mainly public because it's used to build [Structure Together](https://github.com/DustinWehr/structure-together-app). I have written minimal documentation, but will write more if anyone else is interested. **

Minimally-expressive macros for Typescript/Javascript, appropriate for inlining and/or stripping custom print/log/assertion/timing commands (i.e. void function calls; see [the macros I use](./test/structure_together_macros.ts) for [Structure Together](https://github.com/DustinWehr/structure-together-app) for  examples). The main benefit of the inlining is so your custom commands don't make your browser's source code links and stack traces less useful or more cluttered.

Has a simple multiple file watching solution, so you don't need to integrate it into your build script. Instead, you (easily) set it up to run on the final js file outputs of your build script, either overwriting the file (recommended unless you're _not_ generating any javascript) or writing to a file of the same name but with ".out.js" instead of ".js".

Essentially all it does is inline or strip commands according to a [simple configuration file](./innocent_macros_src/YOUR_PROJECT_SPECIFC_MAIN_FILE_TO_MODIFY.py), where the action to be done can depend on a build key and the watched file. Commands can use a ...rest parameter. For anything else more complex, you'll want to use [sweet.js](https://www.sweetjs.org/).

Design constraints:

* Don't parse to an AST, for the sake of simplicity and speed. 
* The pre-macro-expanded code should be valid TypeScript/JavaScript that does basically the same thing as the expanded code. So you don't ever NEED to run the expand/strip script.
* Preserves line numbers. This isn't a hard constraint, in that if someone wants to add support for source maps, or explain to me why it's really easy so I can do it myself, I'm on board.

## Usage
First set at least the two path variables at the top of `innocent_macros_src/YOUR_PROJECT_SPECIFIC_MAIN_FILE_TO_MODIFY.py`. That should be enough to run the tests. Then:

    python3 innocent_macros_src/YOUR_PROJECT_SPECIFIC_MAIN_FILE_TO_MODIFY.py -h
If that works, make a copy of `YOUR_PROJECT_SPECIFIC_MAIN_FILE_TO_MODIFY.py`, put it in your project's repo, and set the remaining configuration options in it.

## Improvements I'll do if there is interest
1. Put the Typescript-specific code behind an interface, so this project can be used to add "innocent macros" to other languages.
2. More documentation.

## Contributions Wanted
1. Anything in "Improvements I'll do if there is interest".
2. Any organization or style improvements. Just please don't use highly-abbreviated names. 

## Contributing
I'm likely to accept any pull request that doesn't make the project technically worse. 

Check the issues to make sure somebody isn't already working on it. Then make an issue for what you want to work on.  

## Tests
This project does not yet use a testing library, but you can run it on the source code for which it was developed as follows.

First set the two path variables at the top of `innocent_macros_src/YOUR_PROJECT_SPECIFIC_MAIN_FILE_TO_MODIFY.py`. 
    python3 test/run_tests.py
