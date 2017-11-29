# -*- coding: utf-8 -*-
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.lib.cache.localcache import localcache


class Handler(BattleEventBaseHandler):
    """バトルイベントプレゼント一覧.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        now = OSAUtil.get_now()
        
        model_mgr = self.getModelMgr()
        
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        cur_eventmaster = None
        if config.mid and config.starttime <= now < config.epilogue_endtime:
            cur_eventmaster = BackendApi.get_battleevent_master(model_mgr, config.mid, using=settings.DB_READONLY)
        
        if cur_eventmaster is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return
        elif config.starttime <= now < config.endtime:
            self.checkBattleEventUser(do_check_battle_open=False, do_check_regist=False)
            if self.response.isEnd:
                return
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 現在の贈り物情報を確認.
        cur_number = None
        presentdata = BackendApi.get_battleeventpresent_pointdata(model_mgr, uid, cur_eventmaster.id, using=settings.DB_READONLY)
        if presentdata:
            cur_data = presentdata.getData()
            cur_number = cur_data['number']
        self.html_param['cur_number'] = cur_number
        
        client = localcache.Client()
        key = 'battleeventpresent_contentlist:%s' % config.mid
        obj_contentlist = client.get(key)
        if obj_contentlist is None:
            presentmasterlist = BackendApi.get_battleeventpresent_master_by_eventdid(model_mgr, config.mid, using=settings.DB_READONLY).values()
            presentmasterlist.sort(key=lambda x:x.number)
            
            obj_contentlist = []
            for presentmaster in presentmasterlist:
                tmp_dict = dict(presentmaster.contents)
                contentmasterlist = BackendApi.get_battleeventpresent_content_master_list(model_mgr, tmp_dict.keys(), using=settings.DB_READONLY)
                contentmasterlist.sort(key=lambda x:x.pri, reverse=True)
                prizeinfo_list = []
                for contentmaster in contentmasterlist:
                    prizelist = BackendApi.get_prizelist(model_mgr, contentmaster.prizes, using=settings.DB_READONLY)
                    prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
                    prizeinfo['name'] = contentmaster.name
                    prizeinfo_list.append(prizeinfo)
                obj = Objects.battleevent_present_content(self, presentmaster, prizeinfo_list)
                obj_contentlist.append(obj)
            client.set(key, obj_contentlist)
        self.html_param['battleeventpresent_contentlist'] = obj_contentlist
        
        # 贈り物確認のリンク.
        url = UrlMaker.battleevent_present()
        self.html_param['url_battleevent_present'] = self.makeAppLinkUrl(url)
        
        # イベント情報.
        self.html_param['battleevent'] = Objects.battleevent(self, cur_eventmaster, now)
        
        # HTML書き出し.
        self.writeAppHtml('%s/presentlist' % ('gcevent' if cur_eventmaster.is_goukon else 'btevent'))
    

def main(request):
    return Handler.run(request)
