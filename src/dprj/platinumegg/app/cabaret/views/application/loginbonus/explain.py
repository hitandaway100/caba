# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.loginbonus.base import LoginBonusHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.rediscache import LoginBonusTimeLimitedAnimationSet


class Handler(LoginBonusHandler):
    """ロングログインボーナスの説明ページ.
    """
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        args = self.getUrlArgs('/lbtlexplain/')
        mid = args.getInt(0)
        
        config = BackendApi.get_current_loginbonustimelimitedconfig(model_mgr, using=settings.DB_READONLY)
        
        master = None
        if not mid:
            data = config.getData()
            if data:
                mid = data['mid']
        if mid:
            master = BackendApi.get_loginbonustimelimitedmaster(model_mgr, mid, using=settings.DB_READONLY)
        
        datadict = dict(config.getDataList())
        config_data = datadict.get(mid)
        
        if master is None or config_data is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return
        
        now = OSAUtil.get_now()
        obj_longlogin = Objects.longloginbonus(config_data, 0, now)
        self.html_param['longloginbonus'] = obj_longlogin
        
        # 開催中か.
        is_open = obj_longlogin['is_open']
        if is_open:
            if BackendApi.check_lead_loginbonustimelimited(model_mgr, uid, now):
                self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
                return
            
            # 現在のログイン日数.
            logindata = BackendApi.get_logintimelimited_data(model_mgr, uid, mid, using=settings.DB_READONLY)
            cur_day = logindata.days
            obj_longlogin['cur_day'] = cur_day
            
            table = BackendApi.get_loginbonustimelimiteddaysmaster_day_table_by_timelimitedmid(model_mgr, mid, using=settings.DB_READONLY)
            days = table.keys()
            days.sort()
            
            tmp_days = list(set(days + [cur_day]))
            tmp_days.sort()
            
            idx = tmp_days.index(cur_day)
            if not cur_day in days:
                idx -= 1
            
            # 直近の報酬.
            if 0 <= idx < len(days):
                daysmaster_id = table[days[idx]]
                daysmaster = BackendApi.get_loginbonustimelimiteddaysmaster_by_id(model_mgr, daysmaster_id, using=settings.DB_READONLY)
                if daysmaster:
                    self.html_param['longloginbonus_daydata'] = Objects.longloginbonus_daydata(daysmaster.day, self.getBonusItemList(daysmaster), cur_day)
            
            # 次の報酬.
            idx += 1
            if 0 <= idx < len(days):
                daysmaster_id = table[days[idx]]
                daysmaster = BackendApi.get_loginbonustimelimiteddaysmaster_by_id(model_mgr, daysmaster_id, using=settings.DB_READONLY)
                if daysmaster:
                    self.html_param['longloginbonus_daydata_next'] = Objects.longloginbonus_daydata(daysmaster.day, self.getBonusItemList(daysmaster), cur_day)
        
        self.writeAppHtml(master.htmlname)
    
    def getBonusItemList(self, master):
        """ログインボーナスのテキストを作成
        """
        if LoginBonusTimeLimitedAnimationSet.exists(master.mid, master.day):
            items = LoginBonusTimeLimitedAnimationSet.get(master.mid, master.day)
        else:
            model_mgr = self.getModelMgr()
            prizelist = BackendApi.get_prizelist(model_mgr, master.prizes, using=settings.DB_READONLY)
            prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
            items = [listitem['text'] for listitem in prizeinfo['listitem_list']]
            LoginBonusTimeLimitedAnimationSet.save(master.mid, master.day, items)
        return items

def main(request):
    return Handler.run(request)
