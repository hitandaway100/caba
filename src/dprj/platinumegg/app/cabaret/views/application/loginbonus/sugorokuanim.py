# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.views.application.loginbonus.base import LoginBonusHandler
from platinumegg.lib.opensocial.util import OSAUtil
import settings
import urllib
from defines import Defines


class Handler(LoginBonusHandler):
    """双六ログインボーナス演出.
    """
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        args = self.getUrlArgs('/lbsugorokuanim/')
        mid = args.getInt(0)
        page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
        loginbonus = args.getInt(1)
        
        model_mgr = self.getModelMgr()
        now = OSAUtil.get_now()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        viewer_id = v_player.id
        
        if BackendApi.check_lead_loginbonus_sugoroku(model_mgr, viewer_id, now):
            # まだ受け取っていない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'まだ受け取っていない')
            url = self.makeAppLinkUrlRedirect(UrlMaker.loginbonussugorokudo())
            self.appRedirect(url)
            return
        logindata = BackendApi.get_loginbonus_sugoroku_playerdata(model_mgr, viewer_id, mid, using=settings.DB_DEFAULT)
        if logindata is None:
            url = self.makeAppLinkUrlRedirect(UrlMaker.mypage())
            self.appRedirect(url)
            return
        
        squares_id_list = logindata.result.get('square_id_list')
        squares_master_list = BackendApi.get_loginbonus_sugoroku_map_squares_master_list_by_id(model_mgr, squares_id_list, using=settings.DB_READONLY)
        squares_master_list.sort(key=lambda x:squares_id_list.index(x.id))
        mapidlist = []
        mapid = None
        for squares_master in squares_master_list:
            if mapid is None or mapid != squares_master.mid:
                mapid = squares_master.mid
                mapidlist.append(mapid)
        page_max = len(mapidlist)
        mapmaster = BackendApi.get_loginbonus_sugoroku_map_master(model_mgr, mapidlist[page], using=settings.DB_READONLY)
        # 飛び先のURL.
        if page_max < 2 or page_max <= (page + 1):
            url = self.makeNextEffectUrl(loginbonus, timelimited=True, comeback=False, sugoroku=mid)
            url = self.makeAppLinkUrl(url)
        else:
            url = UrlMaker.loginbonussugorokuanim(mid, loginbonus)
            url = OSAUtil.addQuery(url, Defines.URLQUERY_PAGE, page+1)
            url = self.makeAppLinkUrl(url)
        dataUrl = self.makeAppLinkUrlEffectParamGet('sugoroku/{}/{}'.format(mid, page))
        self.appRedirectToEffect2('{}/effect2.html'.format(mapmaster.effectname), dataUrl, dataBody=urllib.urlencode(dict(backUrl=url)))

def main(request):
    return Handler.run(request)
