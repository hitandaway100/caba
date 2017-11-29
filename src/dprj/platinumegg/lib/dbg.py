# -*- coding: utf-8 -*-
import settings_sub
import logging
import datetime
import os

class DbgLogger:
    
    def __init__(self):
        self.__logs = []
    
    def __format(self, loglevel, msg):
        if type(msg) is not unicode:
            m = unicode(msg, 'utf-8')
        else:
            m = msg
        return u'[%s]%s' % (loglevel, m)
    
    def trace(self, msg):
        if settings_sub.IS_DEV and settings_sub.USE_LOG:
            self.__logs.append(self.__format(u'TRACE', msg))
            logging.debug(msg)
    
    def info(self, msg):
        if settings_sub.USE_LOG:
            self.__logs.append(self.__format(u'INFO', msg))
        logging.info(msg)
    
    def warning(self, msg):
        if settings_sub.USE_LOG:
            self.__logs.append(self.__format(u'WARNING', msg))
        logging.warn(msg)
    
    def error(self, msg):
        if settings_sub.USE_LOG:
            self.__logs.append(self.__format(u'ERROR', msg))
        DbgLogger.write_error(msg)
    
    def to_string(self, sep='\n'):
        return sep.join(self.__logs)
    
    @staticmethod
    def write_error(msg):
        logging.error(msg)
        DbgLogger.write_app_log('%s_error' % settings_sub.APP_NAME, msg)
    
    @staticmethod
    def write_app_log(filename_base=settings_sub.APP_NAME, value=u''):
        # 追記型にする.
        # ずっと貯めこみたくないので5日毎にファイル作成.
        f = None
        try:
            if not os.path.exists(settings_sub.ERR_LOG_PATH):
                os.mkdir(settings_sub.ERR_LOG_PATH)
            now = datetime.datetime.now()
            filename = '%s_%s.log' % (filename_base, now.strftime('%Y%m%d'))
            f = open(os.path.join(settings_sub.ERR_LOG_PATH, filename), 'a')
            f.write('%s%s' % (now.strftime("[%Y-%m-%d %H:%M:%S]\n"), value))
            f.write('\n')
            f.write('\n')
            f.close()
        except:
            if f != None:
                f.close()
                f = None

