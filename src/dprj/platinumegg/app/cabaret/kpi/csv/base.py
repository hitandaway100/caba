# -*- coding: utf-8 -*-
import os
from platinumegg.lib.strutil import StrUtil
from platinumegg.lib.opensocial.util import OSAUtil


class KpiCSVBase:
    def __init__(self, date, output_dir):
        self.__date = date
        self.__output_dir = output_dir
    
    @property
    def date(self):
        return self.__date
    
    @property
    def output_dir(self):
        return self.__output_dir
    
    @classmethod
    def get_name(cls):
        name = '_'.join(cls.__module__.split('.kpi.csv.')[-1].split('.'))
        return name
    
    def get_data(self):
        pass
    
    def delete(self):
        pass
    
    def write_file(self, csvfilepath, csv_data):
        f = None
        try:
            f = open(csvfilepath, "w")
            f.write(csv_data)
            f.close()
        except:
            if f:
                f.close()
                f = None
            raise
    
    def get_csvdirname(self):
        return self.get_name()
    
    def make_csvfilename(self):
        strdate = self.date.strftime("%Y%m%d")
        csvfilename = '%s_%s.csv' % (self.get_name(), strdate)
        return csvfilename
    
    def write(self):
        output_dir = os.path.join(self.output_dir, self.get_csvdirname())
        
        data = self.get_data()
        if data is None:
            print 'data not found..'
        else:
            # csv作成.
            csvfilename = self.make_csvfilename()
            
            def makeRow(row):
                arr = []
                for v in row:
                    s = u'%s' % v
                    s = s.replace('"', '""')
                    arr.append(u'"%s"' % s)
                return u','.join(arr)
            rows = [makeRow(row) for row in data]
            csv_data = StrUtil.to_s(u'\n'.join(rows), dest_enc='shift-jis')
            
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            
            filepath = os.path.join(output_dir, csvfilename)
            self.write_file(filepath, csv_data)
            print 'Output:%s' % filepath
            
            strnow = OSAUtil.get_now().strftime("%Y%m%d")
            if strnow != self.date.strftime("%Y%m%d"):
                self.delete()
