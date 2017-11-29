# -*- coding: utf-8 -*-
import threading

class ThreadResult:
    """スレッドの結果を保持.
    """
    def __init__(self, result, error):
        self.__result = result
        self.__error = error
    
    def get(self):
        """保持されてるデータを返す.
        スレッド処理で例外が発生していた場合はその例外が投げられる.
        """
        if self.__error == None:
            return self.__result
        raise self.__error

class ThreadBase(threading.Thread):
    """エラー考慮したThread.
    """
    
    @property
    def result(self):
        return self.__result
    @property
    def error(self):
        return self.__error
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.__result = None
        self.__error = None
    
    def run(self):
        try:
            self.__result = self.work()
        except Exception, err:
            self.__error = err
    
    def work(self):
        return None

class ThreadMethod(ThreadBase):
    """メソッドをスレッド実行.
    """
    
    def __init__(self, method, *args, **kwargs):
        ThreadBase.__init__(self)
        self.__method = method
        self.__args = args
        self.__kwargs = kwargs
    
    def work(self):
        method = self.__method
        args = self.__args
        kwargs = self.__kwargs
        return method(*args, **kwargs)
