# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(AppHandler):
    """行動履歴.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        page = 0
        
        v_player = self.getViewerPlayer()
        try:
            if self.is_pc:
                oid = int(self.request.get(Defines.URLQUERY_ID) or v_player.id)
                content_num = Defines.PC_GAMELOG_CONTENT_NUM
            else:
                args = self.getUrlArgs('/playerlog/')
                oid = int(args.get(0, v_player.id))
                page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
                content_num = Defines.GAMELOG_PAGE_CONTENT_NUM
        except:
            raise CabaretError(u'閲覧できません', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        
        offset = page * content_num
        limit = content_num + 1
        obj_playerlog_list = BackendApi.get_playerlog_list(self, oid, offset, limit, model_mgr, using=settings.DB_READONLY)
        
        self.execute_api()
        
        if self.is_pc:
            self.json_result_param['playerlog_list'] = obj_playerlog_list[:content_num]
            self.writeAppJson()
        else:
            has_next_page = content_num < len(obj_playerlog_list)
            self.html_param['playerlog_list'] = obj_playerlog_list[:content_num]
            
            url_base = UrlMaker.playerlog(oid)
            if 0 < page:
                url = OSAUtil.addQuery(url_base, Defines.URLQUERY_PAGE, page - 1)
                self.html_param['url_prev'] = self.makeAppLinkUrl(url)
            
            if has_next_page:
                url = OSAUtil.addQuery(url_base, Defines.URLQUERY_PAGE, page + 1)
                self.html_param['url_next'] = self.makeAppLinkUrl(url)
            
            lognum = BackendApi.get_playerlog_num(model_mgr, oid, using=settings.DB_READONLY)
            self.html_param['cur_page'] = page + 1
            self.html_param['page_max'] = max(1, int((lognum + Defines.GAMELOG_PAGE_CONTENT_NUM - 1) / Defines.GAMELOG_PAGE_CONTENT_NUM))
            
            self.writeAppHtml('playerlog')
    

def main(request):
    return Handler.run(request)
