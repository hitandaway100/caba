# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines


class LoginBonusHandler(AppHandler):
    """ログインボーナスのハンドラ.
    """
    @staticmethod
    def getEffectBackUrl(handler):
        model_mgr = handler.getModelMgr()
        v_player = handler.getViewerPlayer()
        uid = v_player.id
        
        if BackendApi.check_raidevent_lead_opening(model_mgr, uid, using=settings.DB_READONLY):
            # イベントOPを見ないといけない.
            url = UrlMaker.raidevent_opening()
        elif BackendApi.check_raidevent_lead_bigboss(model_mgr, uid, using=settings.DB_READONLY):
            # 大ボス演出を見ないといけない.
            url = UrlMaker.raidevent_bigboss()
        elif BackendApi.check_scoutevent_lead_opening(model_mgr, uid, using=settings.DB_READONLY):
            # イベントOPを見ないといけない.
            url = UrlMaker.scoutevent_opening()
        elif BackendApi.check_battleevent_lead_opening(model_mgr, uid, using=settings.DB_READONLY):
            # イベントOPを見ないといけない.
            url = UrlMaker.battleevent_opening()
        elif not BackendApi.check_battleevent_loginbonus_received(model_mgr, uid, using=settings.DB_READONLY, now=OSAUtil.get_now()):
            # イベントログインボーナスを受け取らないといけない.
            url = UrlMaker.battleevent_loginbonus()
        else:
            url = UrlMaker.present()
        return url
    
    def getBackUrl(self):
        return self.getEffectBackUrl(self)
    
    def makeNextEffectUrl(self, loginbonus=False, timelimited=False, comeback=False, sugoroku=False):
        arr = [
            (Defines.URLQUERY_ID1, comeback, UrlMaker.comebackanim),
            (Defines.URLQUERY_ID2, sugoroku, UrlMaker.loginbonussugorokuanim),
            (Defines.URLQUERY_ID, timelimited, UrlMaker.loginbonustimelimitedanim),
        ]
        def make_baseurl(v, cur_mid, urlmaker):
            midlist = [int(str_mid) for str_mid in v.split(',') if str_mid.isdigit()]
            next_mid = self.findNext(midlist, cur_mid)
            return urlmaker(next_mid, loginbonus) if next_mid is not None else None
        querystring = ''
        baseurl = None
        first = None
        for key,flag,urlmaker in arr:
            if flag is False:
                continue
            v = self.request.get(key)
            if v:
                if baseurl is None:
                    if type(flag) in {int, long}:
                        cur_mid = flag
                        baseurl = make_baseurl(v, cur_mid, urlmaker)
                    else:
                        first = first or (v, urlmaker)
                querystring = OSAUtil.addQuery(querystring, key, v)

        if baseurl is None and first:
            v, urlmaker = first
            baseurl = make_baseurl(v, 0, urlmaker)
        if baseurl:
            sep = '?' if baseurl.find('?') == -1 else '&'
            return baseurl + sep + querystring[1:]
        elif loginbonus:
            return UrlMaker.loginbonusanim()
        else:
            return self.getBackUrl()
    
    def addComeBackResultQueryString(self, url, comeback):
        """カムバック演出用のクエリをつける.
        """
        if not comeback:
            return url
        
        str_mid_list = [str(mid) for mid in list(set(comeback))]
        url = OSAUtil.addQuery(url, Defines.URLQUERY_ID1, ','.join(str_mid_list))
        return url
    
    def addTimeLimitedResultQueryString(self, url, timelimited_result):
        """ロングログイン演出用のクエリをつける.
        """
        if not timelimited_result:
            return url
        
        if isinstance(timelimited_result, dict):
            timelimited_result = [timelimited_result]
        
        str_midlist = []
        for resultdata in timelimited_result:
            bonusmaster = resultdata.get('bonusmaster')
            if not (bonusmaster and bonusmaster.prizes):
                continue
            str_midlist.append(str(resultdata['master'].id))
        
        if str_midlist:
            url = OSAUtil.addQuery(url, Defines.URLQUERY_ID, ','.join(str_midlist))
        return url
    
    def makeUrlByTimeLimitedResult(self, timelimited_result, loginbonus=True):
        """ロングログイン書込結果から演出のURLを作成.
        """
        if not timelimited_result:
            return None
        
        if isinstance(timelimited_result, dict):
            timelimited_result = [timelimited_result]
        
        url = None
        resultdata_first = None
        
        str_midlist = []
        for resultdata in timelimited_result:
            bonusmaster = resultdata.get('bonusmaster')
            if not (bonusmaster and bonusmaster.prizes):
                continue
            elif resultdata_first is None:
                resultdata_first = resultdata
            str_midlist.append(str(resultdata['master'].id))
        
        if resultdata_first:
            bonusmaster = resultdata_first.get('bonusmaster')
            master = resultdata_first.get('master')
            url = UrlMaker.loginbonustimelimitedanim(master.id, loginbonus)
        return url
    
    def addSugorokuResultQueryString(self, url, sugoroku_result):
        """双六ログイン演出用のクエリをつける.
        """
        if not sugoroku_result:
            return url
        str_midlist = [str(master.id) for master in sugoroku_result]
        url = OSAUtil.addQuery(url, Defines.URLQUERY_ID2, ','.join(str_midlist))
        return url
    
    def makeUrlBySugorokuResult(self, sugoroku_result, loginbonus=True):
        """双六ログイン書込結果から演出のURLを作成.
        """
        if not sugoroku_result:
            return None
        url = None
        if sugoroku_result:
            url = UrlMaker.loginbonussugorokuanim(sugoroku_result[0].id, loginbonus)
        return url
    
    def findNext(self, midlist, cur_mid=0):
        if not midlist:
            return None
        elif cur_mid == 0:
            return midlist[0]
        
        if cur_mid in midlist:
            next_idx = midlist.index(cur_mid)+1
            if next_idx < len(midlist):
                return midlist[next_idx]
        return None
