# -*- coding: utf-8 -*-
from platinumegg.lib.strutil import StrUtil


class CSVWriter():
    def __init__(self, path, keep_maxlength=50000):
        self._path = path
        self._size = 0
        self._data = []
        self._keep_maxlength = keep_maxlength
        self.output(overwrite=True)
    
    def makeRow(self, row):
        arr = []
        for v in row:
            s = u'%s' % v
            s = s.replace('"', '""')
            arr.append(u'"%s"' % s)
        return u','.join(arr)
    
    def add(self, row):
        text = self.makeRow(row)
        self._data.append(text)
        self._size += len(text)     # 厳密には違うけど..
        if self._keep_maxlength <= self._size:
            self.output(overwrite=False)
            self._data = []
            self._size = 0
    
    def output(self, overwrite=False):
        if self._data:
            self._data.append('')
        data_str = StrUtil.to_s('\n'.join(self._data), 'shift-jis')
        if overwrite:
            mode = 'w'
        else:
            mode = 'a'
        f = None
        try:
            f = open(self._path, mode)
            f.write(data_str)
            f.close()
        except:
            if f:
                f.close()
            raise
