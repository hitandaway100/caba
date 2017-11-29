# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
import settings


class Handler(AppHandler):
    """運営からのお知らせ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        args = self.getUrlArgs('/infomation/')
        self.__args = args
        
        procname = args.get(0)
        table = {
            'list' : self.procList,
            'detail' : self.procDetail,
        }
        proc = table.get(procname, None)
        if proc is None:
            self.response.set_status(404)
            self.response.end()
        else:
            proc()
    
    def procList(self):
        """一覧表示.
        """
        page = 0
        try:
            page = int(self.request.get(Defines.URLQUERY_PAGE, 0))
        except:
            pass
        
        infomation_list, infomation_num = BackendApi.get_infomations(self, page, using=settings.DB_READONLY)
        has_next_page = Defines.INFORMATION_PAGE_CONTENT_NUM < len(infomation_list)
        infomation_list = infomation_list[:Defines.INFORMATION_PAGE_CONTENT_NUM]
        self.html_param['infomations'] = [Objects.infomation(self, infomation) for infomation in infomation_list]
        
        url_base = UrlMaker.infomation()
        if 0 < page:
            url = OSAUtil.addQuery(url_base, Defines.URLQUERY_PAGE, page - 1)
            self.html_param['url_prev'] = self.makeAppLinkUrl(url)
        
        if has_next_page:
            url = OSAUtil.addQuery(url_base, Defines.URLQUERY_PAGE, page + 1)
            self.html_param['url_next'] = self.makeAppLinkUrl(url)
        
        # ページ情報
        self.html_param['cur_page'] = page + 1
        self.html_param['page_max'] = max(1, int((infomation_num + Defines.INFORMATION_PAGE_CONTENT_NUM - 1) / Defines.INFORMATION_PAGE_CONTENT_NUM))
        self.writeAppHtml('infomation')
    
    def procDetail(self):
        """詳細表示.
        """
        mid = 0
        try:
            mid = int(self.__args.get(1))
        except:
            pass
        
        infomation = None
        if 0 < mid:
            model_mgr = self.getModelMgr()
            infomation = BackendApi.get_infomation(model_mgr, mid, using=settings.DB_READONLY)
        
        if infomation is None:
            self.response.set_status(404)
            self.response.end()
            return
        
        # バナーの埋め込み
        if '${jumpto}' in infomation.body and '${imageurl}' in infomation.body:
            jumpto = self.makeAppLinkUrl(infomation.jumpto)
            imageurl = self.url_static_img + infomation.imageurl
            infomation.body = infomation.body.replace('${jumpto}', jumpto).replace('${imageurl}', imageurl)

        self.html_param['infomation'] = Objects.infomation(self, infomation)
        
        self.writeAppHtml('infodetail')

def main(request):
    return Handler.run(request)
