from warnings import warn
try:
    import csv
except ImportError:
    warn('module \'csv\' could not be imported!')

class Matr(list):

    def __new__(self, file = None, data = [], dtype = None):
        return super().__new__(self, data)

    def __init__(self, file = None, data = [], dtype = None):
        # super().__init__(Matr.fromfile(file, dtype = dtype) if file and not data else data)
        if file and not data:
            super().__init__(Matr.fromfile(file, dtype = dtype))
        else:
            super().__init__(data)
        self.file = file
        self.dtype = dtype

    def __getitem__(self, val):
        if not isinstance(val, tuple):
            ret = super().__getitem__(self.indrow(val))
            if not isinstance(ret, Matr):
                ret = Matr(data = ret)
            ret.dtype = self.dtype
            return ret
        if __debug__:
            assert len(val) == 2, 'cant have a getitem of length more than 2! ' + str(val)
        ret = super().__getitem__(self.indrow(val[0])).__getitem__(self.indcol(val[1]))
        return ret

    def indrow(self, row):
        if isinstance(row, slice):
            return slice(self.indrow(row.start),\
                         self.indrow(row.stop),\
                         self.indrow(row.step))
        if isinstance(row, int):
            return row
        for i in range(len(self.rows)):
            if row == self[i,0]:
                return i
        return row

    def indcol(self, col):
        if isinstance(col, slice):
            return slice(self.indcol(col.start),\
                         self.indcol(col.stop),\
                         self.indcol(col.step))
        if isinstance(col, int):
            return col
        for i in range(len(self.cols)):
            if col == self[0, i]:
                return i
        return col

    def __repr__(self):
        return "Matr(file={},data={},dtype={})".format(self.file, super().__repr__(), self.dtype)

    # def __str__(self):
    #     ret = "Matrix (file = '{}', dtype = '{}')".format(self.file, self.dtype)
    #     maxl = [max([e for e in col]) for col in self.cols]
    #     print(maxl)
    #     return ret



    def __contains__(self, val):
        return val in self.ids or super().__contains__(val)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type != None:
            raise
        elif self.file != None:
            self >> self.file
        return True

    def __lshift__(self, fout):
        return self.__rrshift__(fout)

    def __rlshift__(self, fout):
        return self.__rshift__(fout)

    def __rrshift__(self, fin):
        """ fin >> self :: Sets self to the Matrix read from the input file"""
        return self.fromfile(fin)

    def __rshift__(self, fout):
        """ self >> fout :: writes self to fout, """
        return self.tofile(fout)

    @staticmethod
    def fromfile(fin, dtype = None, skipchar = '#', splitchar = ','):
        """ splitchar is only when no csv """
        import io
        if isinstance(fin, str):
            file = fin
            fin = csv.reader(open(fin, 'r'))
        elif isinstance(fin, io.IOBase):
            file = fin.name
            fin = csv.reader(fin)
        else:
            raise TypeError("No known way to read from file type '%s'." % type(fin))
        del io

        if __debug__:
            assert hasattr(fin, '__iter__'), 'cannot iterate over type \'{}\'!'.format(type(fin))

        data = []
        dtypes = dtype if hasattr(dtype, "__getitem__") else [dtype] if dtype else [int, float, complex, str]
        for line in fin:
            if not isinstance(line, list):
                if __debug__:
                    assert isinstance(line, str)
                line = line.split(splitchar)

            if not line[0][0] == skipchar:
                data.append(Matr())
                for val in line:
                    for datatype in dtypes:
                        try:
                            data[-1].append(datatype(val))
                            break
                        except ValueError:
                            if dtypes[-1] == datatype:
                                warn("no known way to coerce '{}' into {}!".format(val, dtypes))
                                data[-1].append(val)
        return Matr(file = file, data = data)

    def tofile(self, fout = None):
        if fout == None:
            fout = self.file
        if isinstance(fout, str):
            fout = csv.writer(open(fout, 'w'))
        if __debug__:
            assert hasattr(fout, "writerow") or hasattr(fout, "write") or hasattr(fout, "writeline")
        for row in self:
            row = [str(ele) for ele in row]
            if hasattr(fout, "writerow"): #AKA, if it's a csv writer.
                fout.writerow(row)
            elif hasattr(fout, "writeline"):
                fout.write(",".join(row))
            elif hasattr(fout, "write"):
                fout.write(",".join(row) + '\n')
            else:
                return NotImplemented
        return self

    @property
    def rows(self):
        return self

    @property
    def cols(self):
        ret = Matr(dtype = self.dtype)
        # for row in range(len(self)):
            # for col in range(len(self[0])):

        return ret


    @property
    def headers(self):
        return self[0]

    @property
    def ids(self):
        return [row[0] for row in self][1:]

def main():
    m = Matr() << 'testdata.txt'
    print(type(m[0:]),m[0:])
    # with Matr('testdata.txt') as m:
    #     print(m)
if __name__ == '__main__':
    main()







