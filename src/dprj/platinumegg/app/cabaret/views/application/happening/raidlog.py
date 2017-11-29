# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
import settings
from platinumegg.app.cabaret.models.Player import PlayerTreasure
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventHelpSpecialBonusScore,\
    RaidEventSpecialBonusScoreLog
from platinumegg.app.cabaret.util.happening import HappeningRaidSet, RaidBoss,\
    HappeningUtil
from platinumegg.app.cabaret.util.present import PrizeData

class Handler(HappeningHandler):
    """レイド履歴.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerTreasure]
    
    def process(self):
        
        helplog = None
        args = self.getUrlArgs('/raidlog/')
        logid = str(args.get(0, ''))
        
        model_mgr = self.getModelMgr()
        if logid.isdigit():
            logid = int(logid)
            helplog = BackendApi.get_raidlogs(model_mgr, [logid], using=settings.DB_READONLY).get(logid, None)
        if helplog:
            self.procDetail(helplog)
        else:
            self.procList()
    
    def procList(self):
        """一覧.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        page = 0
        try:
            page = int(self.request.get(Defines.URLQUERY_PAGE, 0))
        except:
            pass
        offset = page * Defines.RAIDLOG_CONTENT_NUM_PER_PAGE
        limit = Defines.RAIDLOG_CONTENT_NUM_PER_PAGE
        raidlogidlist = BackendApi.get_raidlog_idlist(model_mgr, v_player.id, offset, limit, using=settings.DB_READONLY)
        
        raidloglist = BackendApi.get_raidlogs(model_mgr, raidlogidlist, using=settings.DB_READONLY).values()
        cb = BackendApi.put_list_raidlog_obj(self, raidloglist)
        
        # 通知解除.
        if page == 0:
            BackendApi.delete_raidlog_notificationid(v_player.id)
        
        self.execute_api()
        cb()
        
        url = UrlMaker.raidloglist()
        lognum = BackendApi.get_raidlog_num(model_mgr, v_player.id, using=settings.DB_READONLY)
        self.putPagenation(url, page, lognum, Defines.RAIDLOG_CONTENT_NUM_PER_PAGE)
        
        cur_eventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY)
        if cur_eventmaster:
            self.html_param['url_raidevent_top'] = self.makeAppLinkUrl(UrlMaker.raidevent_top(cur_eventmaster.id))
        
        self.writeHtmlSwitchEvent('loglist', basedir_normal='raid')
    
    def procDetail(self, helplog):
        """詳細.
        """
        model_mgr = self.getModelMgr()
        
        v_player = self.getViewerPlayer()

        # レイド情報.
        raidboss = BackendApi.get_raid(model_mgr, helplog.raidid, using=settings.DB_READONLY, get_instance=True)
        is_owner = v_player.id == raidboss.raid.oid
        if not (is_owner or v_player.id in raidboss.getDamageRecordUserIdList()):
            # 閲覧できない.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.happening()))
            return
        
        damagerecord = raidboss.getDamageRecord(v_player.id)
        
        is_cleared = raidboss.raid.hp == 0
        is_canceled = False
        
        prizelist = None
        
        # ハプニング情報.
        happeningset = BackendApi.get_happening(model_mgr, raidboss.id, using=settings.DB_READONLY)
        if happeningset is None:
            BackendApi.save_raidlog_idlist(model_mgr, v_player.id, using=settings.DB_READONLY)
            url = UrlMaker.raidloglist()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # イベント情報を設定.
        BackendApi.reset_raidboss_eventraidmaster(model_mgr, raidboss, happeningset.happening.event, using=settings.DB_READONLY)
        
        raideventmaster = None
        excludes = None
        raideventid = HappeningUtil.get_raideventid(happeningset.happening.event)
        if raideventid:
            raideventmaster = BackendApi.get_raideventmaster(model_mgr, raideventid, using=settings.DB_READONLY)
            
            destroypoint_info = None
            
            if is_cleared:
                bonusscore = 0
                if happeningset.happening.oid == v_player.id:
                    specialscore_obj = BackendApi.get_model(model_mgr, RaidEventSpecialBonusScoreLog, raidboss.id, using=settings.DB_READONLY)
                    if isinstance(specialscore_obj, RaidEventSpecialBonusScoreLog):
                        bonusscore = specialscore_obj.bonusscore
                else:
                    _helpbonusscore = BackendApi.get_raidevent_helpspecialbonusscore(raidboss.id, v_player.id, using=settings.DB_DEFAULT)
                    if isinstance(_helpbonusscore, RaidEventHelpSpecialBonusScore):
                        bonusscore = _helpbonusscore.bonusscore
                destroypoint_info = BackendApi.make_raidevent_destroypoint_info(model_mgr, v_player.id, raideventmaster, HappeningRaidSet(happeningset, raidboss), bonusscore, using=settings.DB_READONLY)

                # MVP.
                mvp_uidlist = raidboss.getMVPList()
                self.html_param['mvp_uidlist'] = mvp_uidlist
                
                self.html_param['destroy_time'] = helplog.ctime
            
            # イベント情報.
            config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
            self.html_param['raidevent'] = Objects.raidevent(self, raideventmaster, config)
            
            # シャンパン.
            if 0 < damagerecord.champagne_num_add:
                self.html_param['champagne_num_pre'] = damagerecord.champagne_num_pre
                self.html_param['champagne_num_post'] = damagerecord.champagne_num_post
                self.html_param['champagne_num_add'] = damagerecord.champagne_num_add
            
            # 素材.
            if 0 < damagerecord.material_num:
                materials = raideventmaster.getMaterialDict()
                material_id = materials.get(raidboss.raideventraidmaster.material)
                if material_id:
                    materialmaster = BackendApi.get_raidevent_materialmaster(model_mgr, material_id, using=settings.DB_READONLY)
                    materialnumdata = BackendApi.get_raidevent_materialdata(model_mgr, v_player.id, using=settings.DB_READONLY)
                    obj = Objects.raidevent_material(self, materialmaster, materialnumdata.getMaterialNum(raideventid, raidboss.raideventraidmaster.material))
                    obj['num_add'] = damagerecord.material_num
                    self.html_param['material'] = obj
            
            self.html_param['destroypoint_info'] = destroypoint_info
        elif raidboss.scouteventraidmaster:
            scouteventid = raidboss.scouteventraidmaster.eventid
            tanzaku_number = raidboss.get_tanzaku_number(v_player.id)
            tanzakumaster = BackendApi.get_scoutevent_tanzakumaster(model_mgr, scouteventid, tanzaku_number, using=settings.DB_READONLY) if tanzaku_number is not None else None
            
            if tanzakumaster is not None:
                # 短冊.
                self.html_param['scoutevent_tanzaku'] = Objects.scoutevent_tanzaku(self, tanzakumaster)
                self.html_param['tanzaku_num_pre'] = damagerecord.tanzaku_num_pre
                self.html_param['tanzaku_num_post'] = damagerecord.tanzaku_num_post
                self.html_param['tanzaku_num_add'] = damagerecord.tanzaku_num
        
        if raideventmaster or RaidBoss.RAIDEVENT_PRIZE_UPDATETIME <= happeningset.happening.ctime:
            if is_cleared:
                # 報酬.
                prizelist = []
                if is_owner:
                    # 発見者.
                    if raideventmaster:
                        cabaretking = raidboss.get_cabaretking()
                        if 0 < cabaretking:
                            prizelist.append(PrizeData.create(cabaretking=cabaretking))
                    prizelist.extend(BackendApi.get_prizelist(model_mgr, raidboss.master.prizes, using=settings.DB_READONLY))
                    prizelist.extend(BackendApi.aggregate_happeningprize(happeningset.happening))
                elif 0 < damagerecord.damage_cnt:
                    # 救援者.
                    if raideventmaster:
                        demiworld = raidboss.get_demiworld()
                        if 0 < demiworld:
                            prizelist.append(PrizeData.create(demiworld=demiworld))
                    prizelist = BackendApi.get_prizelist(model_mgr, raidboss.master.helpprizes, using=settings.DB_READONLY)
            elif happeningset.happening.is_canceled() and v_player.id == happeningset.happening.oid:
                # キャンセル.
                prizelist = BackendApi.aggregate_happeningprize(happeningset.happening, cancel=True)
                is_canceled = True
        
        # ダメージ履歴.
        func_put_attacklog = self.putRaidAttackLog(raidboss, excludes=excludes)
        
        prizeinfo = None
        if prizelist:
            prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
        
        persons = {}
        dmmid = ''
        if not is_owner:
            o_players = BackendApi.get_players(self, [happeningset.happening.oid], [], using=settings.DB_READONLY)
            if o_players:
                o_player = o_players[0]
                dmmid = o_player.dmmid
                persons = BackendApi.get_dmmplayers(self, o_players, using=settings.DB_READONLY, do_execute=False)
        
        self.html_param['player'] = Objects.player(self, v_player)
        
        self.html_param['is_cleared'] = is_cleared
        self.html_param['is_canceled'] = is_canceled
        
        self.execute_api()
        
        self.html_param['happening'] = Objects.happening(self, HappeningRaidSet(happeningset, raidboss), prizeinfo, o_person=persons.get(dmmid))
        
        if func_put_attacklog:
            func_put_attacklog()
        
        self.setFromPage(Defines.FromPages.RAIDLOG, helplog.id)
        self.html_param['url_trade'] = self.makeAppLinkUrl(UrlMaker.trade(), add_frompage=True)
        
        self.writeHtmlSwitchEvent('log', eventmaster=raideventmaster, basedir_normal='raid')
    

def main(request):
    return Handler.run(request)
