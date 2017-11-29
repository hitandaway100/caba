# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
import os


class Handler(AppHandler):
    """PC版のテンプレート閲覧TOP.
    """
    def process(self):
        TEMPLATE_FORMAT = '/template_test/pc/%s.html'
        
        # テスト用に欲しいパラメータを並べていく.
        self.html_param.update({
            'url_topimage' : self.makeAppLinkUrlStatic('img/top.jpg'),
            'url_enter' : self.makeAppLinkUrl(TEMPLATE_FORMAT % 'mypage'),
            'infomations' : [],
#            'infomation' : None,
            'slidebanners' : [],
            'eventbanners' : [],
            'power_total' : 100000,
            'card_num' : 100,
            'friend_num' : 10,
            'friendrequest_num' : 5,
            'free_gacha' : True,
            'present_num' : 2,
            'friendlog_list' : [],
            'friendaccept_num' : 1,
            'playerlog_list' : [],
            'greetlog_list' : [],
        })
        
        self.html_param['pc_template_list'] = self.getFilePathList(excludes=['_include', '_styles'])
        
        self.osa_util.write_html('test/pctesttop.html', self.html_param)
    
    def getFilePathList(self, base_path='pc', excludes=None):
        excludes = excludes or []
        dirpath = self.getPath(os.path.join('../templates/', base_path))
        arr = []
        filelist = os.listdir(dirpath)
        
        for filename in filelist:
            if filename in excludes:
                continue
            path = os.path.join(base_path, filename)
            try:
                arr.extend(self.getFilePathList(path))
            except OSError:
                arr.append(path)
        return arr
    
    def get_html_param(self, key, key_test=None):
        htmlname = key_test or key
        url = u'/template_test/%s' % htmlname
        return self.makeAppLinkUrl(url)
    
def main(request):
    return Handler.run(request)
