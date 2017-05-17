from typing import List

class Chunk(object):
    """
    stop_line_stop_ind is None iff stop_line_num is None
    stop_line_stop_ind is INCLUSIVE
    A Chunk is "open" iff stop_line_num == None. It's "closed" otherwise.
    ...is that a useful distinction though? maybe in that case stop_line_num should just be the last line number of the file?
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
