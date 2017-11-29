# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.lib.opensocial.util import OSAUtil
import datetime

class Handler(BattleEventBaseHandler):
    """バトルイベントランク履歴一覧.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        args = self.getUrlArgs('/battleeventgrouplog/list/')
        eventid = args.getInt(0)
        
        model_mgr = self.getModelMgr()
        eventmaster = None
        if eventid:
            eventmaster = BackendApi.get_battleevent_master(model_mgr, eventid, using=settings.DB_READONLY)
        if eventmaster is None:
            self.redirectToTop()
            return
        
        cur_eventmaster = self.getCurrentBattleEvent(quiet=True)
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        basetime = DateTimeUtil.toLoginTime(OSAUtil.get_now())
        cdate_max = datetime.date(basetime.year, basetime.month, basetime.day)
        if cur_eventmaster and cur_eventmaster.id == eventid:
            cdate_max -= datetime.timedelta(days=1)
        
        # グループ履歴ID.
        rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventid, uid, using=settings.DB_READONLY)
        obj_list = []
        if rankrecord and rankrecord.groups:
            groupidlist = rankrecord.groups[:]
            num = len(groupidlist)
            for idx in xrange(num):
                obj = self.makeRankRecordObj(rankrecord, groupidlist[-(idx+1)], logonly=True, cdate_max=cdate_max)
                if obj:
                    obj_list.append(obj)
        self.html_param['battleevent_rank_list'] = obj_list
        
        self.putEventTopic(eventmaster.id)
        
        if eventmaster.is_goukon:
            self.writeAppHtml('gcevent/rankloglist')
        else:
            self.writeAppHtml('btevent/rankloglist')

def main(request):
    return Handler.run(request)
