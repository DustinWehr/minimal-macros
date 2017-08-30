import re
from copy import copy

from constants import DEBUGGING
from common import split_by_top_level_commas, Chunk, escapeQuotes, couldBeToken, inStrLiteral, updateInStrLit

# This code is intentionally not optimized, because (a) it only runs on small files, and (b) it only runs
# when you change a macro definition.
class MacroDefn:

    """
    self._template - list that alternates between strings and indices* into self._params, starting and ending with a
      string (possibly the empty string, for the first and/or last spots, which can be the same),
      such that if self._template[2i+1] = j, then self._params[j] is the i-th occurrence of a macro function parameter.
    self._param_occurrences - list of pairs (i,j) such that self._body_str[i:j+1] is a valid occurrence of one
      of the macro function parameters.
    self.has_rest_param -
    self.num_optional_params -
    """

    def __init__(self, fnname, params_str, body_str):
        assert isinstance(params_str, str)

        self._fnname = fnname
        self._body_str = body_str

        if DEBUGGING:
            for i in range(len(body_str)):
                if body_str[i] == "`":
                    WarningMsg("Looks like you've used a backquote in a macro definition. As of now, this probably means your code will only run in a js interpreter that supports template strings (es6).")

        possibly_typed_params_list_chunks = split_by_top_level_commas(Chunk.fromSingleLine(params_str))
        possibly_typed_params_list = list(map(lambda x: x.asSingleLine(), possibly_typed_params_list_chunks))

        self._numRestParams = 1 if len(possibly_typed_params_list) > 0 and "..." in possibly_typed_params_list[-1] else 0
        self._numOptionalParams = sum( map( lambda x: 1 if ("?" in x) else 0, possibly_typed_params_list ) )
        self._numParams = len(possibly_typed_params_list)
        self._numRegParams = self._numParams - self._numOptionalParams - self._numRestParams
        self._params = list(map(MacroDefn._parse_typed_param, possibly_typed_params_list))

        self._param2ind = dict()
        for i in range(len(self._params)):
            self._param2ind[self._params[i]] = i

        self._params_re = re.compile("|".join(self._params))
        self._param_occurrences = self._findParamOccurrences()
        if len(self._param_occurrences) == 0:
            self._no_subst = True

        self._fillTemplate()

    def _fillTemplate(self):
        total_occurrences = len(self._param_occurrences)
        self._template = [0] * (2 * total_occurrences + 1)
        if total_occurrences == 0:
            self._template[0] = self._body_str
            return
        else:
            self._template[0] = self._body_str[0: self._param_occurrences[0][0]]

        for i in range(0, total_occurrences):
            (start,end) = self._param_occurrences[i]
            x = self._body_str[start:end + 1]
            assert x in self._params

            param = self._body_str[start:end + 1]
            self._template[2 * i + 1] = self._param2ind[param]

            # rest_stop = _get_start_end_pair(self._param_occurrences[i + 1])[0] if i < total_occurrences - 1 else len(self._body_str)
            rest_stop = self._param_occurrences[i + 1][0] if i < total_occurrences - 1 else len(self._body_str)
            self._template[2 * i + 2] = self._body_str[end + 1 : rest_stop]


    def _findParamOccurrences(self):
        occ = []
        cur_pos = 0
        match = self._params_re.search(self._body_str, cur_pos)
        while match:
            start, end = (match.start(), match.end()-1)

            if not couldBeToken(start, end, self._body_str):
                continue

            occ.append( (start, end) )

            cur_pos = end+1
            match = self._params_re.search(self._body_str, cur_pos)

        return occ;


    def simult_subst(self, args_list):
        paramlist = self._params
        subst = {}

        nParam = self._numParams
        nOpt = self._numOptionalParams
        nRest = self._numRestParams
        nRegParam = self._numRegParams

        nArg = len(args_list)

        assert nArg >= nRegParam, "A function with {0} regular parameters, {1} optional parameters, {2} rest parameter, must have at least {0} arguments".format(nRegParam, nOpt, nRest)

        # required params
        for i in range( nRegParam ):
            p = paramlist[i]
            subst[p] = args_list[i]

        # insert args for optional params, if they were given
        for i in range( nRegParam, min(nRegParam + nOpt, nArg) ):
            p = paramlist[i]
            subst[p] = args_list[i]

        # insert undefined for optional params that didn't get an arg
        for i in range( min(nRegParam + nOpt, nArg), nRegParam + nOpt ):
            p = paramlist[i]
            subst[p] = "undefined"

        if self._numRestParams:
            # for the rest parameter we insert a comma-separated concatenation of the remaining args
            if nArg > nRegParam + nOpt:
                p = paramlist[-1]
                subst[p] = ",".join(args_list[nRegParam+nOpt:])
            # or undefined:
            else:
                p = paramlist[-1]
                subst[p] = "undefined"

        to_fill = copy(self._template)

        for i in range(1,len(self._template),2):
            t = self._template[i]
            if isinstance(t, dict):
                param = self._params[ t[MacroDefn.KEY_ESCAPE_FOR_STR_LITERAL] ]
                to_fill[i] = escapeQuotes( subst[ param ] )
            else:
                param = self._params[ t ]
                to_fill[i] = subst[param]
        
        return "".join(to_fill)



    @staticmethod
    def _parse_typed_param(x):
        if "=" in x:
            raise Exception("Looks like you're using a default argument in a macro definition. Those are not supported.")

        rv = x.split(":")[0].strip()
        if rv[-1] == "?":
            rv = rv[:-1]  # remove the "?"
        elif "?" in rv:
            raise Exception("Found ? in unexpected place, not at the end of the parameter name.")

        if rv.startswith("..."):
            rv = rv[3:] # remove the "..."

        return rv


