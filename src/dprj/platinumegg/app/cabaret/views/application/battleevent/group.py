# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.models.Player import PlayerExp
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventGroupLog
from platinumegg.app.cabaret.util.battleevent import BattleEventGroupUserData

class Handler(BattleEventBaseHandler):
    """バトルイベント本日ランク詳細.
    """
    
    CONTENT_NUM_PER_PAGE = 10
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        eventmaster = self.getCurrentBattleEvent()
        if not self.checkBattleEventUser(do_check_battle_open=False):
            return
        
        model_mgr = self.getModelMgr()
        group = self.getCurrentBattleGroup(do_search_log=True)
        page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
        rankmaster = BackendApi.get_battleevent_rankmaster_byId(model_mgr, group.rankid, using=settings.DB_READONLY)
        
        if rankmaster is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.battleevent_top(eventmaster.id)))
            return
        
        now = OSAUtil.get_now()
        eventid = eventmaster.id
        
        if isinstance(group, BattleEventGroupLog):
            userdatalist = group.userdata
        else:
            scorerecords = BackendApi.get_battleevent_scorerecord_dict(model_mgr, eventid, group.useridlist[:], get_instance=True, using=settings.DB_READONLY)
            scorerecord_list = scorerecords.values()
            scorerecord_list.sort(key=lambda x:x.getPointToday(now), reverse=True)
            userdatalist = []
            pointpre = None
            for idx,scorerecord in enumerate(scorerecord_list):
                point = scorerecord.getPointToday(now)
                if pointpre is None or point < pointpre:
                    rank = idx + 1
                    pointpre = point
                userdata = BattleEventGroupUserData.createByScoreRecord(scorerecord, rank, now)
                userdatalist.append(userdata)
        userdatalist.sort(key=lambda x:x.grouprank)
        
        nummax = len(userdatalist)
        offset = page * Handler.CONTENT_NUM_PER_PAGE
        targetlist = userdatalist[offset:(offset + Handler.CONTENT_NUM_PER_PAGE)]
        
        obj_playerlist = []
        if targetlist:
            uidlist = [data.uid for data in targetlist]
            playerlist = BackendApi.get_players(self, uidlist, [PlayerExp], using=settings.DB_READONLY)
            obj_player_dict = dict([(obj_player['id'], obj_player) for obj_player in self.getObjPlayerList(playerlist)])
            
            for data in targetlist:
                obj_player = obj_player_dict.get(data.uid)
                if obj_player:
                    obj_player['event_rank'] = data.grouprank
                    obj_player['event_score'] = data.point
                    obj_player['is_me'] = uid == data.uid
                    obj_playerlist.append(obj_player)
        self.html_param['playerlist'] = obj_playerlist
        
        self.putPagenation(UrlMaker.battleevent_group(), page, nummax, Handler.CONTENT_NUM_PER_PAGE)
        
        self.putEventTopic(eventid)
        
        rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, rankmaster.eventid, uid, using=settings.DB_READONLY)
        self.html_param['battleevent_rank'] = Objects.battleevent_rank(self, rankrecord, rankmaster, group)
        
        if eventmaster.is_goukon:
            self.writeAppHtml('gcevent/grouprank')
        else:
            self.writeAppHtml('btevent/grouprank')

def main(request):
    return Handler.run(request)
