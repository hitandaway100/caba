# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventGroup,\
    BattleEventGroupLog, BattleEventRankMaster, BattleEventMaster,\
    BattleEventScore
import datetime
from platinumegg.app.cabaret.util.battleevent import BattleEventGroupUserData
from defines import Defines

class Handler(AdminHandler):
    """バトルイベントグループ閲覧確認.
    """
    def process(self):
        args = self.getUrlArgs('/infomations/view_battleevent_group/')
        
        self.html_param['url_view_battleevent_group'] = self.makeAppLinkUrlAdmin(UrlMaker.view_battleevent_group())
        
        groupid = args.getInt(0)
        if groupid:
            self.__procView(groupid)
        else:
            self.__procSearch()
    
    def __getGroupRecord(self, groupidlist):
        grouplist = BattleEventGroup.getByKey(groupidlist, using=settings.DB_READONLY)
        grouploglist = BattleEventGroupLog.getByKey(groupidlist, using=settings.DB_READONLY)
        modellist = list(grouplist) + list(grouploglist)
        modellist.sort(key=lambda x:x.cdate, reverse=True)
        return modellist
    
    def __getGroupRecordByRank(self, eventid, rank, cdate):
        rankid = BattleEventRankMaster.makeID(eventid, rank)
        grouplist = BattleEventGroup.fetchValues(filters={'rankid':rankid,'cdate':cdate}, using=settings.DB_READONLY)
        grouploglist = BattleEventGroupLog.fetchValues(filters={'rankid':rankid,'cdate':cdate}, using=settings.DB_READONLY)
        modellist = list(grouplist) + list(grouploglist)
        modellist.sort(key=lambda x:x.cdate, reverse=True)
        return modellist
    
    def __procSearch(self):
        """グループ検索.
        """
        def to_i(v):
            if str(v).isdigit():
                return int(v)
            else:
                return None
        
        eventid = to_i(self.request.get('_eventid'))
        
        serchtype = self.request.get('_serchtype')
        value = self.request.get('_value')
        page = (to_i(self.request.get('_page')) or 0)
        cdate = self.request.get('_cdate')
        
        model_mgr = self.getModelMgr()
        
        target_uid = None
        grouplist = None
        if serchtype == 'uid':
            uid = to_i(value)
            rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventid, uid, using=settings.DB_READONLY)
            if rankrecord and rankrecord.groupidlist:
                grouplist = self.__getGroupRecord(rankrecord.groupidlist)
                target_uid = uid
            else:
                grouplist = []
        elif serchtype == 'dmmid':
            uid = BackendApi.dmmid_to_appuid(self, [value], using=settings.DB_READONLY).get(value)
            grouplist = []
            if uid:
                rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventid, uid, using=settings.DB_READONLY)
                if rankrecord and rankrecord.groupidlist:
                    grouplist = self.__getGroupRecord(rankrecord.groupidlist)
                    target_uid = uid
        elif serchtype == 'rank':
            cdatetime = datetime.datetime.strptime(cdate, "%Y-%m-%d")
            grouplist = self.__getGroupRecordByRank(eventid, to_i(value) or 1, datetime.date(cdatetime.year, cdatetime.month, cdatetime.day))
        elif serchtype == 'groupid':
            groupidlist = [to_i(str_id) for str_id in value.split(',') if to_i(str_id)]
            grouplist = self.__getGroupRecord(groupidlist)
        
        if grouplist is not None:
            if not grouplist:
                self.putAlertToHtmlParam(u'見つかりませんでした', AlertCode.INFO)
            else:
                
                rank_all = dict([(master.id, master) for master in BackendApi.get_battleevent_rankmaster_by_eventid(model_mgr, eventid, using=settings.DB_READONLY, do_check_open=False)])
                
                PAGE_CONTENT_NUM = 100
                offset = page * PAGE_CONTENT_NUM
                contentnum = len(grouplist)
                page_max = int((contentnum + PAGE_CONTENT_NUM - 1) / PAGE_CONTENT_NUM)
                grouplist = grouplist[offset:(offset+PAGE_CONTENT_NUM)]
                
                obj_list = []
                for group in grouplist:
                    rankmaster = rank_all[group.rankid]
                    is_end = isinstance(group, BattleEventGroupLog)
                    if isinstance(group, BattleEventGroup):
                        usernum = len(group.useridlist)
                    else:
                        usernum = len(group.userdata)
                    
                    obj_userdata = None
                    if is_end and target_uid:
                        # 終了していればユーザーのデータも設定.
                        for userdata in group.userdata:
                            if userdata.uid != target_uid:
                                continue
                            obj_userdata = {
                                'point' : userdata.point,
                                'fame' : userdata.fame,
                                'winmax' : userdata.win,
                                'rankup' : userdata.rankup,
                                'grouprank' : userdata.grouprank,
                            }
                            break
                    
                    data = {
                        'id' : group.id,
                        'rankid' : rankmaster.id,
                        'rankname' : rankmaster.name,
                        'usernum' : usernum,
                        'cdate' : group.cdate.strftime("%Y/%m/%d"),
                        'url' : self.makeAppLinkUrlAdmin(UrlMaker.view_battleevent_group(group.id)),
                        'userdata' : obj_userdata,
                        'is_end' : is_end,
                    }
                    obj_list.append(data)
                self.html_param['grouplist'] = obj_list
                
                url = UrlMaker.view_battleevent_group()
                url = OSAUtil.addQuery(url, '_eventid', eventid)
                url = OSAUtil.addQuery(url, '_serchtype', serchtype)
                url = OSAUtil.addQuery(url, '_value', value)
                url = OSAUtil.addQuery(url, '_cdate', cdate)
                self.html_param['pagination'] = self.makePagenationData(url, page, page_max)
                
                self.html_param['eventid'] = eventid
                self.html_param['serchtype'] = serchtype
                self.html_param['value'] = value
                self.html_param['cdate'] = cdate or ''
        
        self.html_param['battleeventlist'] = model_mgr.get_mastermodel_all(BattleEventMaster, order_by='id', using=settings.DB_READONLY)
        
        self.html_param['target_uid'] = target_uid
        
        self.writeAppHtml('infomations/view_battleevent/search')
    
    def __procView(self, groupid):
        """詳細表示.
        """
        CONTENT_NUM_PER_PAGE = 20
        page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
        
        now = OSAUtil.get_now()
        
        model_mgr = self.getModelMgr()
        
        grouplist = self.__getGroupRecord([groupid])
        if not grouplist:
            self.putAlertToHtmlParam(u'見つかりませんでした', AlertCode.ERROR)
            self.__procSearch()
            return
        
        group = grouplist[0]
        eventmaster = BackendApi.get_battleevent_master(model_mgr, group.eventid, using=settings.DB_READONLY)
        rankmaster = BackendApi.get_battleevent_rankmaster_byId(model_mgr, group.rankid, using=settings.DB_READONLY)
        
        is_end = isinstance(group, BattleEventGroupLog)
        obj_group = {
            'id' : group.id,
            'eventid' : eventmaster.id,
            'eventname' : eventmaster.name,
            'rankid' : rankmaster.id,
            'rank' : rankmaster.rank,
            'rankname' : rankmaster.name,
            'usernum' : 10,
            'usernummax' : rankmaster.membernummax,
            'cdate' : group.cdate.strftime("%Y/%m/%d"),
            'is_end' : is_end,
        }
        self.html_param['group'] = obj_group
        
        # 参加しているユーザー.
        if isinstance(group, BattleEventGroup):
            uidlist = group.useridlist
            scorerecordlist = BattleEventScore.getInstanceByKey([BattleEventScore.makeID(uid, eventmaster.id) for uid in uidlist], using=settings.DB_READONLY)
            scorerecordlist.sort(key=lambda x:x.getPointToday(now), reverse=True)
            
            userdatalist = []
            rank = 0
            pointpre = None
            for idx,scorerecord in enumerate(scorerecordlist):
                point = scorerecord.getPointToday(now)
                if pointpre is None or point < pointpre:
                    rank = idx + 1
                
                userdata = BattleEventGroupUserData.createByScoreRecord(scorerecord, rank, now)
                userdatalist.append(userdata)
                
                pointpre = point
        else:
            userdatalist = group.userdata
        
        page_max = (len(userdatalist)+CONTENT_NUM_PER_PAGE-1) / CONTENT_NUM_PER_PAGE
        
        offset = page * CONTENT_NUM_PER_PAGE
        userdatalist = userdatalist[offset:(offset+CONTENT_NUM_PER_PAGE)]
        
        userdata_dict = dict([(userdata.uid, userdata) for userdata in userdatalist])
        playerlist = BackendApi.get_players(self, userdata_dict.keys(), [], using=settings.DB_READONLY)
        persons = BackendApi.get_dmmplayers(self, playerlist, using=settings.DB_READONLY)
        
        obj_playerlist = []
        for player in playerlist:
            obj_player = self.makeListPlayer(player, persons[player.dmmid], userdata_dict[player.id])
            obj_playerlist.append(obj_player)
        obj_playerlist.sort(key=lambda x:x['grouprank'])
        self.html_param['playerlist'] = obj_playerlist
        
        url = UrlMaker.view_battleevent_group(groupid)
        self.html_param['pagination'] = self.makePagenationData(url, page, page_max)
        
        self.writeAppHtml('infomations/view_battleevent/detail')
    
    def makeListPlayer(self, player, person, userdata):
        return {
            'id' : player.id,
            'person' : Objects.person(self, player, person),
            'dmmid' : player.dmmid,
            'point' : userdata.point,
            'fame' : userdata.fame,
            'winmax' : userdata.win,
            'rankup' : userdata.rankup,
            'grouprank' : userdata.grouprank,
            'url' : self.makeAppLinkUrlAdmin(UrlMaker.view_player(player.id)),
        }
    
    def makePagenationData(self, url, page, page_max):
        def __makePage(index):
            return {
                'num':index+1,
                'url':self.makeAppLinkUrlAdmin(OSAUtil.addQuery(url, '_page', index)),
            }
        pagination_data = {
            'page_list':[__makePage(p) for p in xrange(0, page_max)],
            'now_page':__makePage(page),
            'has_next':False,
            'has_prev':False,
        }
        if (page+1) < page_max:
            pagination_data['next_page'] = __makePage(page+1)
            pagination_data['has_next'] = True
        if 0 < page:
            pagination_data['prev_page'] = __makePage(page-1)
            pagination_data['has_prev'] = True
        return pagination_data

def main(request):
    return Handler.run(request)
