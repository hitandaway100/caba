# -*- coding: utf-8 -*-

class UrlArgs:
    """REST指定の部分のURLは実際には引数なので、その部分を取得するためのクラス
    """

    
    def __init__(self, base_path, request_path):
        """
        basepath, reauest path を返す.
        """
        self.args = self.__parseUrl(base_path, request_path)
    
    @staticmethod
    def __parseUrl(base_path, request_path):
        """
        REST部分URLを配列で返す
        """
        path = request_path.replace(base_path, '')
        path = path.split('?', 1)
        
        path = path[0]
        if 0 < len(path):
            return path.split('/')
        else:
            return []
    
    def get(self, index, default_value=''):
        """
        指定した番号のREST形式引数を返してやる
        なかった場合はdefault_valueを返す
        """
        dest = None
        if index < len(self.args):
            dest = self.args[index]
        if dest is None or dest == '':
            dest = default_value
        return dest
    
    def getInt(self, index):
        s = str(self.get(index))
        if s.isdigit():
            return int(s)
        else:
            return None
    
    def length(self):
        return len(self.args)
    