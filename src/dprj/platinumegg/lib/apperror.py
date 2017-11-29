# -*- coding: utf-8 -*-
import traceback
import sys

class AppError(Exception):
    
    STATUS_UNKNOWN = 0xffff
    
    def __init__(self, value='', code=STATUS_UNKNOWN):
        self.code = code
        self.value = value
    def __str__(self):
        return repr(self.value)
    def getHtml(self, is_developer=False):
        if is_developer or not self._isDeveloperOnlyStatus():
            return self.value
        else:
            return u'ｴﾗｰが発生しました'
    
    def _isDeveloperOnlyStatus(self):
        return True
    
    @staticmethod
    def makeErrorTraceString(info):
        t = str(info[0]).replace('<', '').replace('>','')
        ex = '%s:%s' % (t, info[1])
        t_list = traceback.extract_tb(info[2])
        trace = ''
        for t in t_list:
            trace += '%s:%s\n- %s\n' % (t[0], t[1], t[2])
        return trace + '\n%s\n' % ex

class ErrorUtil:
    @staticmethod
    def getLastErrorMessage():
        """
        sys.exc_info()[1] という表記がよくわかんないのでラップした.
        
        ex)
        try
            # なんか処理
        except:
            print(ErrorUtil.getLastErrorMessage())
        
        """
        info = sys.exc_info()
        t = str(info[0]).replace('<', '').replace('>','')
        return '%s:%s' % (t, info[1])
