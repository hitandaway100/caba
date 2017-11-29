# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.models.Player import PlayerExp
from defines import Defines

class Handler(BattleEventBaseHandler):
    """バトルイベントランク履歴詳細.
    """
    
    CONTENT_NUM_PER_PAGE = 10
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        args = self.getUrlArgs('/battleeventgrouplog/detail/')
        groupid = args.getInt(0)
        page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
        
        model_mgr = self.getModelMgr()
        grouplog = None
        eventmaster = None
        rankmaster = None
        if groupid:
            grouplog = BackendApi.get_battleevent_grouplog(model_mgr, groupid, using=settings.DB_READONLY)
            if grouplog:
                rankmaster = BackendApi.get_battleevent_rankmaster_byId(model_mgr, grouplog.rankid, using=settings.DB_READONLY)
                if rankmaster:
                    eventmaster = BackendApi.get_battleevent_master(model_mgr, rankmaster.eventid, using=settings.DB_READONLY)
        
        if eventmaster is None:
            self.redirectToTop()
            return
        
        grouplog.userdata.sort(key=lambda x:x.point, reverse=True)
        
        nummax = len(grouplog.userdata)
        offset = page * Handler.CONTENT_NUM_PER_PAGE
        targetlist = grouplog.userdata[offset:(offset + Handler.CONTENT_NUM_PER_PAGE)]
        obj_playerlist = []
        if targetlist:
            pointlist = [data.point for data in grouplog.userdata]
            uidlist = [data.uid for data in targetlist]
            playerlist = BackendApi.get_players(self, uidlist, [PlayerExp], using=settings.DB_READONLY)
            obj_player_dict = dict([(obj_player['id'], obj_player) for obj_player in self.getObjPlayerList(playerlist)])
            
            rank = pointlist.index(targetlist[0].point)
            point = None
            for data in targetlist:
                if point is None or data.point < point:
                    rank += 1
                point = data.point
                obj_player = obj_player_dict.get(data.uid)
                if obj_player:
                    obj_player['event_rank'] = rank
                    obj_player['event_score'] = data.point
                    obj_player['is_me'] = data.uid == uid
                    obj_playerlist.append(obj_player)
        self.html_param['playerlist'] = obj_playerlist
        
        self.putPagenation(UrlMaker.battleevent_grouplogdetail(groupid), page, nummax, Handler.CONTENT_NUM_PER_PAGE)
        
        self.putEventTopic(rankmaster.eventid)
        
        self.html_param['url_battleevent_ranklog'] = self.makeAppLinkUrl(UrlMaker.battleevent_grouploglist(rankmaster.eventid))
        
        rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, rankmaster.eventid, uid, using=settings.DB_READONLY)
        self.html_param['battleevent_rank'] = Objects.battleevent_rank(self, rankrecord, rankmaster, grouplog)
        
        if eventmaster.is_goukon:
            self.writeAppHtml('gcevent/ranklog')
        else:
            self.writeAppHtml('btevent/ranklog')

def main(request):
    return Handler.run(request)
