# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.alert import AlertCode
from defines import Defines
from platinumegg.app.cabaret.models.Happening import RaidMaster, Happening, Raid
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.happening import HappeningUtil

class Handler(AdminHandler):
    """レイド情報確認.
    """
    def process(self):
        args = self.getUrlArgs('/infomations/view_raid/')
        
        self.html_param['HappeningState'] = Defines.HappeningState
        self.html_param['url_view_raid'] = self.makeAppLinkUrlAdmin(UrlMaker.view_raid())
        
        raid = str(args.get(0))
        if raid.isdigit():
            self.__procView(int(raid))
        else:
            self.__procSearch()
    
    def __procSearch(self):
        """レイド検索.
        """
        def to_i(v):
            if str(v).isdigit():
                return int(v)
            else:
                return None
        
        serchtype = self.request.get('_serchtype')
        value = self.request.get('_value')
        state = to_i(self.request.get('_state')) or Defines.HappeningState.END
        page = (to_i(self.request.get('_page')) or 0)
        
        model_mgr = self.getModelMgr()
        raid_all = dict([(master.id, master) for master in model_mgr.get_mastermodel_all(RaidMaster, fetch_deleted=True, using=settings.DB_READONLY)])
        
        uid = None
        if serchtype == 'uid':
            uid = to_i(value)
        elif serchtype == 'dmmid':
            uid = BackendApi.dmmid_to_appuid(self, [value], using=settings.DB_READONLY).get(value)
        
        if uid:
            PAGE_CONTENT_NUM = 100
            
            filters = {
                'oid' : uid,
                'state' : state,
            }
            nummax = Happening.count(filters, using=settings.DB_READONLY)
            page_max = (nummax + PAGE_CONTENT_NUM - 1) / PAGE_CONTENT_NUM
            
            offset = page * PAGE_CONTENT_NUM
            recordlist = Happening.fetchValues(filters=filters, order_by='-ctime', limit=PAGE_CONTENT_NUM, offset=offset, using=settings.DB_READONLY)
            raiddict = BackendApi.get_model_dict(model_mgr, Raid, [record.id for record in recordlist], using=settings.DB_READONLY)
            
            raidlist = []
            for record in recordlist:
                raid = raiddict.get(record.id)
                master = None
                if raid:
                    master = raid_all.get(record.mid)
                
                if master:
                    raidlist.append({
                        'id' : record.id,
                        'mid' : master.id,
                        'name' : master.name,
                        'level' : record.level,
                        'ctime' : DateTimeUtil.dateTimeToStr(record.ctime),
                        'url' : self.makeAppLinkUrlAdmin(UrlMaker.view_raid(record.id))
                    })
                else:
                    raidlist.append({
                        'id' : record.id,
                        'mid' : record.mid,
                        'name' : u'不明',
                        'level' : record.level,
                        'ctime' : DateTimeUtil.dateTimeToStr(record.ctime),
                        'url' : None
                    })
            
            url = UrlMaker.view_raid()
            url = OSAUtil.addQuery(url, '_serchtype', serchtype)
            url = OSAUtil.addQuery(url, '_value', value)
            url = OSAUtil.addQuery(url, '_state', state)
            
            def __makePage(index):
                return {
                    'num':index,
                    'url':self.makeAppLinkUrlAdmin(OSAUtil.addQuery(url, '_page', index-1)),
                }
            pagination_data = {
                'page_list':[__makePage(p) for p in xrange(1, page_max)],
                'now_page':__makePage(page+1),
                'has_next':False,
                'has_prev':False,
            }
            if page < page_max:
                pagination_data['next_page'] = __makePage(page + 1)
                pagination_data['has_next'] = True
            if 1 < page:
                pagination_data['prev_page'] = __makePage(page - 1)
                pagination_data['has_prev'] = True
            self.html_param['pagination'] = pagination_data
            
            self.html_param['raidlist'] = raidlist
        
        self.html_param['serchtype'] = serchtype
        self.html_param['state'] = state
        self.html_param['value'] = value
        
        self.writeAppHtml('infomations/view_raid/search')
    
    def __procView(self, raidid):
        """詳細表示.
        """
        model_mgr = self.getModelMgr()
        
        happeningraidset = BackendApi.get_happeningraidset(model_mgr, raidid, using=settings.DB_READONLY)
        if not happeningraidset:
            self.putAlertToHtmlParam(u'見つかりませんでした', AlertCode.ERROR)
            self.__procSearch()
            return
        
        happeningset = happeningraidset.happening
        
        eventmaster = None
        raidevent_id = HappeningUtil.get_raideventid(happeningset.happening.event)
        if raidevent_id:
            eventmaster = BackendApi.get_raideventmaster(model_mgr, raidevent_id, using=settings.DB_READONLY)
        
        # レイド詳細.
        raidboss = happeningraidset.raidboss
        BackendApi.reset_raidboss_eventraidmaster(model_mgr, raidboss, happeningset.happening.event, using=settings.DB_READONLY)
        
        member_uidlist = list(set(raidboss.getDamageRecordUserIdList() + [raidboss.raid.oid]))
        playerlist = BackendApi.get_players(self, member_uidlist, [], using=settings.DB_READONLY)
        tmp = BackendApi.get_dmmplayers(self, playerlist, using=settings.DB_READONLY)
        players = dict([(player.id, player) for player in playerlist])
        persons = dict([(player.id, tmp.get(player.dmmid)) for player in playerlist])
        
        self.html_param['raid'] = self.makeRaidObj(happeningraidset, players[raidboss.raid.oid], persons.get(raidboss.raid.oid), eventmaster)
        
        mvpuidlist = []
        helppoints = {}
        if eventmaster:
            mvpuidlist = raidboss.getMVPList()
            helppoints = raidboss.getHelpEventPoints()
            self.html_param['event'] = {
                'id' : eventmaster.id,
                'name' : eventmaster.name,
            }
        
        # 秘宝ボーナス.
        fastbonusdata = BackendApi.get_raidevent_fastbonusdata(eventmaster, raidboss, happeningset.happening.etime)
        rate = 1
        if fastbonusdata:
            rate = fastbonusdata['rate']
        
        # ダメージ履歴.
        obj_playerlist = []
        for player in playerlist:
            record = raidboss.getDamageRecord(player.id)
            
            obj_player = self.makeListPlayer(player)
            obj_player['name'] = Objects.person(self, player, persons.get(player.id))['nickname']
            obj_player['damage'] = record.damage
            
            ownerpoint = 0
            mvppoint = 0
            helppoint = 0
            
            if eventmaster and raidboss.hp < 1:
                if player.id == raidboss.raid.oid:
                    ownerpoint = raidboss.get_owner_eventpoint() * rate
                else:
                    helppoint = helppoints.get(player.id, 0) * rate
                
                if player.id in mvpuidlist:
                    mvppoint = raidboss.get_mvp_eventpoint() * rate
            
            obj_player['eventpoints'] = {
                'owner' : ownerpoint,
                'mvp' : mvppoint,
                'help' : helppoint,
            }
            
            obj_playerlist.append(obj_player)
        self.html_param['playerlist'] = obj_playerlist
        
        self.writeAppHtml('infomations/view_raid/detail')
    
    def makeListPlayer(self, player):
        return {
            'id' : player.id,
            'dmmid' : player.dmmid,
            'url' : self.makeAppLinkUrlAdmin(UrlMaker.view_player(player.id)),
        }
    
    def makeRaidObj(self, happeningraidset, o_player, o_person, eventmaster):
        happeningset = happeningraidset.happening
        raidboss = happeningraidset.raidboss
        
        eventdata = None
        if eventmaster:
            fastbonusdata = BackendApi.get_raidevent_fastbonusdata(eventmaster, raidboss, happeningset.happening.etime)
            rate = 1
            if fastbonusdata:
                rate = fastbonusdata['rate']
            
            # コンボボーナス.
            now = OSAUtil.get_now()
            combobonus_rate = BackendApi.get_raidevent_combobonus_powuprate(self.getModelMgr(), eventmaster, raidboss, using=settings.DB_READONLY, now=now)
            combo_cnt = raidboss.getCurrentComboCount(now=now)
            combobonus_rate_next = BackendApi.choice_raidevent_combobonus_powuprate(eventmaster, combo_cnt+1)
            last_uid = None
            
            lastrecord = raidboss.getLastDamageRecord()
            if lastrecord:
                last_uid = lastrecord.uid
            
            combobonus = {
                'cnt' : combo_cnt,
                'powup' : combobonus_rate,
                'powup_next' : combobonus_rate_next,
                'etime' : DateTimeUtil.dateTimeToStr(raidboss.combo_etime),
                'last_uid' : last_uid,
            }
            
            eventdata = {
                'id' : eventmaster.id,
                'name' : eventmaster.name,
                'owner' : raidboss.get_owner_eventpoint() * rate,
                'mvp' : raidboss.get_mvp_eventpoint() * rate,
                'combobonus' : combobonus,
            }
        
        oname = Objects.person(self, o_player, o_person)['nickname']
        
        return {
            'id' : happeningset.id,
            'mid' : raidboss.raid.mid,
            'oid' : raidboss.raid.oid,
            'oname' : oname,
            'name' : raidboss.master.name,
            'level' : raidboss.raid.level,
            'hp' : raidboss.hp,
            'hpmax' : raidboss.get_maxhp(),
            'ctime' : DateTimeUtil.dateTimeToStr(happeningset.happening.ctime),
            'etime' : DateTimeUtil.dateTimeToStr(happeningset.happening.etime),
            'state' : Defines.HappeningState.MGR_NAMES.get(happeningset.happening.state),
            'eventdata' : eventdata,
        }

def main(request):
    return Handler.run(request)
