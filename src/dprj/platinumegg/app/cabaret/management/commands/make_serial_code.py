# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.lib.strutil import StrUtil
import os
from platinumegg.lib.pljson import Json
from platinumegg.lib.compression import intCompress
import random

class Command(BaseCommand):
    """シリアル番号の発行.
    """
    class Writer():
        def __init__(self, path, keep_maxlength=50000):
            self._path = path
            self._size = 0
            self._data = []
            self._keep_maxlength = keep_maxlength
            self.output(overwrite=True)
        
        def add(self, text):
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
    
    def handle(self, *args, **options):
        
        print '================================'
        print 'make_serial_code'
        print '================================'
        
        CODE = 'EKY2J8P4BFLWMQZ0UX915HC73NVGAS6TR'
        PATTERN_NUM_MAX = 42618442977
        INTERVAL = 3163483
        OFFSET_1 = 12061
        OFFSET_2 = 14206147659
        
        # 個数.
        num = int(args[0])
        
        # 出力先.
        writer = Command.Writer(args[1])
        
        # index.
        index_filepath = os.path.join(os.path.dirname(__file__), '../../../../../../../tool/serial_index')
        lap = 0
        index = 0
        if os.path.exists(index_filepath):
            f = open(index_filepath, 'r')
            strjson = f.read()
            f.close()
            obj = Json.decode(strjson)
            lap, index = obj
        
        print 'Start from...lap=%d, index=%d' % (lap, index)
        
        def compress(v, length):
            s = intCompress(v, base=CODE)
            if length < len(s):
                raise 'OverFlow!!'
            s = '%s%s' % (CODE[0]*length, s)
            return s[-length:]
        
        # シリアル作成.
        serials = {}
        for _ in xrange(num):
            v0 = random.randint(0, 1088)
            v1 = ((index + OFFSET_1) * INTERVAL) % PATTERN_NUM_MAX
            v2 = ((index + OFFSET_2) * INTERVAL) % PATTERN_NUM_MAX
            
            s0 = compress(v0, 2)
            s1 = compress(v1, 7)
            s2 = compress(v2, 7)
            
            s = s0 + s1 + s2
            if serials.has_key(s):
                raise 'dupplicate...'
            serials[s] = True
            writer.add(s)
            
            index += 1
            if PATTERN_NUM_MAX <= index:
                raise 'index over...'
        
        writer.output(overwrite=False)
        
        # indexを保存.
        print '================================'
        strjson = Json.encode([lap, index])
        print 'write index...%s' % strjson
        f = open(index_filepath, 'w')
        f.write(strjson)
        f.close()
        
        print '================================'
        print 'all done..'
    
