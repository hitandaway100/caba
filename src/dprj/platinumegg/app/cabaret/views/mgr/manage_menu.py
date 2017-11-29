# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.lib.opensocial.util import OSAUtil
import os
import settings_sub
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from defines import Defines
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util, rediscache
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.app.cabaret.models.Item import ItemMaster
from platinumegg.app.cabaret.models.Card import CardMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.present import PrizeData
from django.db.models import Max
from platinumegg.app.cabaret.models.Player import PlayerExp, Player
from platinumegg.app.cabaret.util.redisdb import RedisModel, SubProcessPid,\
    LastViewArea
from platinumegg.lib.pljson import Json
from platinumegg.app.cabaret.models.CabaretClubEvent import CabaClubRankEventMaster
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import ProduceEventMaster
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventMaster
from platinumegg.lib.command import CommandUtil
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventMaster
import datetime
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventMaster
from platinumegg.app.cabaret.models.AccessBonus import LoginBonusTimeLimitedMaster,\
    LoginBonusSugorokuMaster
from platinumegg.lib.dbg import DbgLogger
from platinumegg.app.cabaret.models.ComeBack import ComeBackCampaignMaster
from platinumegg.app.cabaret.models.PresentEveryone import PresentEveryoneMypageMaster,\
    PresentEveryoneRecord
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from platinumegg.app.cabaret.models.Present import PrizeMaster
from platinumegg.lib.cache.localcache import localcache
from platinumegg.app.cabaret.models.Infomation import InfomationMaster
from platinumegg.app.cabaret.util.rediscache import InfomationMasterIdListCache
from platinumegg.app.cabaret.models.AppConfig import MessageQueue
from platinumegg.lib.strutil import StrUtil
from platinumegg.lib import timezone

class Handler(AdminHandler):
    """管理機能一覧ページ.
    """
    
    def process(self):
        
        method = self.request.get('method', None)
        f = getattr(self, '_proc_%s' % method, None)
        if f:
            f()
            if self.response.isEnd:
                return
        
        # 初期化.
        self._init_setAppConfig()
        self._init_setPreRegistConfig()
        self._init_setCabaClubRankEventConfig()
        self._init_setProduceEventConfig()
        self._init_setRaidEventConfig()
        self._init_setScoutEventConfig()
        self._init_setBattleEventConfig()
        self._init_setTotalLoginBonusConfig()
        self._init_setLoginBonusTimeLimitedConfig()
        self._init_setComeBackCampaignConfig()
        
        model_mgr = self.getModelMgr()
        
        # 秘宝交換リセットの予約時間.
        resettime = BackendApi.get_trade_resettime(model_mgr, using=settings.DB_READONLY)
        self.html_param['trade_resettime'] = resettime
        
        self.html_param['now_date_str'] = OSAUtil.get_now().strftime("%Y-%m-%d")
        
        # ローカルだとうまくアップできないので代わりに見に行く場所指定.
        self.__local_datafileurl = os.path.join(settings_sub.TMP_DOC_ROOT, 'master_data.json')
        self.html_param['local_datafileurl'] = self.__local_datafileurl
        
        self.html_param['itemlist'] = model_mgr.get_mastermodel_all(ItemMaster, 'id', using=settings.DB_READONLY)
        self.html_param['cardlist'] = model_mgr.get_mastermodel_all(CardMaster, 'id', using=settings.DB_READONLY)
        self.html_param['prizelist'] = model_mgr.get_mastermodel_all(PrizeMaster, 'id', using=settings.DB_READONLY)
        self.html_param['textlist'] = model_mgr.get_mastermodel_all(TextMaster, 'id', using=settings.DB_READONLY)
        self.html_param['cabaclubrankeventlist'] = model_mgr.get_mastermodel_all(CabaClubRankEventMaster, 'id', using=settings.DB_READONLY)
        self.html_param['produceevent_list'] = model_mgr.get_mastermodel_all(ProduceEventMaster, 'id', using=settings.DB_READONLY)
        self.html_param['raideventlist'] = model_mgr.get_mastermodel_all(RaidEventMaster, 'id', using=settings.DB_READONLY)
        self.html_param['scouteventlist'] = model_mgr.get_mastermodel_all(ScoutEventMaster, 'id', using=settings.DB_READONLY)
        self.html_param['battleeventlist'] = model_mgr.get_mastermodel_all(BattleEventMaster, 'id', using=settings.DB_READONLY)
        self.html_param['loginbonustimelimitedlist'] = model_mgr.get_mastermodel_all(LoginBonusTimeLimitedMaster, 'id', using=settings.DB_READONLY)
        self.html_param['loginbonussugorokulist'] = model_mgr.get_mastermodel_all(LoginBonusSugorokuMaster, 'id', using=settings.DB_READONLY)
        self.html_param['comebackcampaignlist'] = model_mgr.get_mastermodel_all(ComeBackCampaignMaster, 'id', using=settings.DB_READONLY)
        self.html_param['infomationlist'] = model_mgr.get_mastermodel_all(InfomationMaster, 'id', using=settings.DB_READONLY)
        self.html_param['messagelist'] = MessageQueue.fetchValues(order_by='id', using=settings.DB_READONLY)
        
        self.html_param['now'] = OSAUtil.get_now()
        
        self.writeAppHtml('manage_menu')
    
    def _init_setAppConfig(self):
        """AppConfigの設定.
        """
        model_mgr = self.getModelMgr()
        app_config = BackendApi.get_appconfig(model_mgr, using=settings.DB_DEFAULT)
        self.html_param['app_config'] = {
            'is_emergency':app_config.is_emergency(),
            'is_platform_maintenance':app_config.is_platform_maintenance(),
            'stime':DateTimeUtil.dateTimeToStr(app_config.stime),
            'etime':DateTimeUtil.dateTimeToStr(app_config.etime),
        }
    
    def _init_setPreRegistConfig(self):
        """事前登録の設定パラメータを取得.
        """
        model_mgr = self.getModelMgr()
        config = BackendApi.get_preregistconfig(model_mgr)
        self.html_param['preregist_config'] = {
            'is_before_publication':config.is_before_publication(),
            'etime':DateTimeUtil.dateTimeToStr(config.etime),
            'prizes':Json.encode(config.prizes),
        }

    def _init_setCabaClubRankEventConfig(self):
        """経営イベントの設定パラメータを取得."""
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_cabaclubrankeventconfig(model_mgr)
        is_opened = False
        now = OSAUtil.get_now()
        if config.mid:
            eventmaster = BackendApi.get_cabaclubrankeventmaster(model_mgr, config.mid, using=settings.DB_READONLY)
            if eventmaster:
                name = eventmaster.name
            else:
                name = u'不明'
            is_opened = config.starttime <= now < config.endtime
        else:
            name = u'無し'

        self.html_param['cabaclubrankevent_config'] = {
            'mid': config.mid,
            'name': name,
            'is_opened': is_opened,
            'stime':config.starttime.strftime('%Y%W'),
            'etime':config.endtime.strftime('%Y%W'),
            'next_stime':config.next_starttime.strftime('%Y%W'),
            'next_etime':config.next_endtime.strftime('%Y%W'),
            'now': now.strftime('%Y%W'),
        }

    def _init_setProduceEventConfig(self):
        """プロデュースイベントの設定パラメータを取得."""
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_produce_event_config(model_mgr)
        is_opened = False
        now = OSAUtil.get_now()
        if config.mid:
            eventmaster = BackendApi.get_produce_event_master(model_mgr, config.mid, using=settings.DB_READONLY)
            if eventmaster:
                name = eventmaster.name
            else:
                name = u'不明'
            is_opened = config.starttime <= now < config.endtime
        else:
            name = u'無し'

        self.html_param['produceevent_config'] = {
            'mid': config.mid,
            'name': name,
            'is_opened': is_opened,
            'is_end': config.endtime <= OSAUtil.get_now(),
            'stime':DateTimeUtil.dateTimeToStr(config.starttime),
            'etime':DateTimeUtil.dateTimeToStr(config.endtime),
            'bigtime':DateTimeUtil.dateTimeToStr(config.bigtime),
            'epilogue_endtime':DateTimeUtil.dateTimeToStr(config.epilogue_endtime),
            'is_exists_closeevent_process' : SubProcessPid.exists(Defines.CLOSE_EVENT_PRODUCE_NAME),
        }

    def _init_setRaidEventConfig(self):
        """レイドイベントの設定パラメータを取得.
        """
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_raideventconfig(model_mgr)
        is_opened = False
        now = OSAUtil.get_now()
        if config.mid:
            eventmaster = BackendApi.get_raideventmaster(model_mgr, config.mid, using=settings.DB_READONLY)
            if eventmaster:
                name = eventmaster.name
            else:
                name = u'不明'
            is_opened = config.starttime <= now < config.endtime
        else:
            name = u'無し'
        
        obj_datalist = []
        for data in config.stageschedule or []:
            obj_datalist.append({
                'stage' : data['stage'],
                'time':DateTimeUtil.dateTimeToStr(data['time']),
            })
        
        self.html_param['raidevent_config'] = {
            'mid':config.mid,
            'name' : name,
            'is_opened' : is_opened,
            'is_end' : config.endtime <= OSAUtil.get_now(),
            'is_big_opened' : BackendApi.check_raidevent_bigboss_opened(model_mgr, now, using=settings.DB_READONLY),
            'stime':DateTimeUtil.dateTimeToStr(config.starttime),
            'etime':DateTimeUtil.dateTimeToStr(config.endtime),
            'bigtime':DateTimeUtil.dateTimeToStr(config.bigtime or config.endtime),
            'ticket_endtime':DateTimeUtil.dateTimeToStr(config.ticket_endtime or config.endtime),
            'is_exists_closeevent_process' : SubProcessPid.exists(Defines.CLOSE_EVENT_PROCESS_NAME),
            'timebonus_time' : Json.encode(config.timebonus_time),
            'combobonus_opentime' : Json.encode(config.combobonus_opentime),
            'feverchance_opentime' : Json.encode(config.feverchance_opentime),
            'fastbonus_opentime' : Json.encode(config.fastbonus_opentime),
            'epilogue_endtime' : DateTimeUtil.dateTimeToStr(config.epilogue_endtime or config.endtime),
            'stageschedule' : obj_datalist,
        }
    
    def _init_setScoutEventConfig(self):
        """スカウトイベントの設定パラメータを取得.
        """
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_scouteventconfig(model_mgr)
        is_opened = False
        now = OSAUtil.get_now()
        if config.mid:
            eventmaster = BackendApi.get_scouteventmaster(model_mgr, config.mid, using=settings.DB_READONLY)
            if eventmaster:
                name = eventmaster.name
            else:
                name = u'不明'
            is_opened = config.starttime <= now < config.endtime
        else:
            name = u'無し'
        
        obj_datalist = []
        for data in config.stageschedule or []:
            obj_datalist.append({
                'stage' : data['stage'],
                'time':DateTimeUtil.dateTimeToStr(data['time']),
            })
        self.html_param['scoutevent_config'] = {
            'mid':config.mid,
            'name' : name,
            'is_opened' : is_opened,
            'is_end' : config.endtime <= OSAUtil.get_now(),
            'stime':DateTimeUtil.dateTimeToStr(config.starttime),
            'etime':DateTimeUtil.dateTimeToStr(config.endtime),
            'is_exists_closeevent_process' : SubProcessPid.exists(Defines.CLOSE_SCOUTEVENT_PROCESS_NAME),
            'epetime':DateTimeUtil.dateTimeToStr(config.epilogue_endtime or config.endtime),
            'stageschedule' : obj_datalist,
            'presentetime':DateTimeUtil.dateTimeToStr(config.present_endtime or config.endtime),
        }
    
    def _init_setBattleEventConfig(self):
        """バトルイベントの設定パラメータを取得.
        """
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_battleeventconfig(model_mgr)
        is_opened = False
        now = OSAUtil.get_now()
        if config.mid:
            eventmaster = BackendApi.get_battleevent_master(model_mgr, config.mid, using=settings.DB_READONLY)
            if eventmaster:
                name = eventmaster.name
            else:
                name = u'不明'
            is_opened = config.starttime <= now < config.endtime
        else:
            name = u'無し'
        
        obj_datalist = []
        for data in config.rankschedule or []:
            obj_datalist.append({
                'rank' : data['rank'],
                'time':DateTimeUtil.dateTimeToStr(data['time']),
            })
        
        self.html_param['battleevent_config'] = {
            'mid':config.mid,
            'name' : name,
            'is_opened' : is_opened,
            'is_end' : config.endtime <= OSAUtil.get_now(),
            'stime':DateTimeUtil.dateTimeToStr(config.starttime),
            'etime':DateTimeUtil.dateTimeToStr(config.endtime),
            'is_emergency' : config.is_emergency,
            'epetime':DateTimeUtil.dateTimeToStr(config.epilogue_endtime),
            'rankschedule' : obj_datalist,
            'ticketetime':DateTimeUtil.dateTimeToStr(config.ticket_endtime)
        }
    
    def _init_setTotalLoginBonusConfig(self):
        """累計ログインボーナスの設定パラメータを取得.
        """
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_totalloginbonusconfig(model_mgr, using=settings.DB_READONLY)
        now = OSAUtil.get_now()
        
        def makeObj(mid, stime, etime=None):
            is_open = False
            etime = etime or OSAUtil.get_datetime_max()
            if mid:
                master = BackendApi.get_loginbonustimelimitedmaster(model_mgr, config.mid, using=settings.DB_READONLY)
                if master:
                    name = master.name
                else:
                    name = u'不明'
                is_open = stime <= now < etime
            else:
                name = u'無し'
            return {
                'mid' : mid,
                'name' : name,
                'is_open' : is_open,
                'stime':DateTimeUtil.dateTimeToStr(stime),
                'etime':DateTimeUtil.dateTimeToStr(etime),
            }
        
        obj = makeObj(config.mid, config.stime, config.etime)
        obj_next = None
        if config.mid_next:
            obj_next = makeObj(config.mid_next, config.etime)
            if obj_next['is_open']:
                obj['current'] = obj_next
            else:
                obj['next'] = obj_next
        
        if config.mid and obj.get('current') is None:
            obj['current'] = dict(obj.items())
        
        obj['mid_next'] = config.mid_next
        obj['continuity_login'] = config.continuity_login
        
        self.html_param['totalloginbonus_config'] = obj
    
    def _init_setLoginBonusTimeLimitedConfig(self):
        """期間付ログインボーナスの設定パラメータを取得.
        """
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_loginbonustimelimitedconfig(model_mgr, using=settings.DB_READONLY)
        now = OSAUtil.get_now()
        
        datalist = config.getDataList()
        obj_datalist = []
        for mid, data in datalist:
            sugoroku = data.get('sugoroku')
            if sugoroku:
                master = BackendApi.get_loginbonus_sugoroku_master(model_mgr, mid, using=settings.DB_READONLY)
            else:
                master = BackendApi.get_loginbonustimelimitedmaster(model_mgr, mid, using=settings.DB_READONLY)
            if master:
                name = master.name
            else:
                name = u'不明'
            is_open = data['stime'] <= now < data['etime']
            obj_datalist.append({
                'mid':mid,
                'name' : name,
                'is_open' : is_open,
                'stime':DateTimeUtil.dateTimeToStr(data['stime']),
                'etime':DateTimeUtil.dateTimeToStr(data['etime']),
                'beginer':data.get('beginer'),
                'sugoroku':sugoroku,
            })
        
        self.html_param['loginbonustimelimited_config'] = obj_datalist
    
    def _init_setComeBackCampaignConfig(self):
        """カムバックキャンペーンの設定パラメータを取得.
        """
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_comebackcampaignconfig(model_mgr, using=settings.DB_READONLY)
        now = OSAUtil.get_now()
        
        datalist = config.getDataList()
        obj_datalist = []
        for mid, data in datalist:
            master = BackendApi.get_comebackcampaignmaster(model_mgr, mid, using=settings.DB_READONLY)
            if master:
                name = master.name
            else:
                name = u'不明'
            is_open = data['stime'] <= now < data['etime']
            obj_datalist.append({
                'mid':mid,
                'name' : name,
                'is_open' : is_open,
                'stime':DateTimeUtil.dateTimeToStr(data['stime']),
                'etime':DateTimeUtil.dateTimeToStr(data['etime']),
            })
        
        self.html_param['comebackcampaign_config'] = obj_datalist
    
    def _proc_set_app_config(self):
        """アプリの設定.
        """
        is_emergency = bool(int(self.request.get('_is_emergency')))
        is_platform_maintenance = bool(int(self.request.get('_is_platform_maintenance')))
        str_maintenance_start = self.request.get('_maintenance_start')
        str_maintenance_end = self.request.get('_maintenance_end')
        
        model_mgr = self.getModelMgr()
        
        stime = DateTimeUtil.strToDateTime(str_maintenance_start)
        etime = DateTimeUtil.strToDateTime(str_maintenance_end)
        app_config = BackendApi.update_appconfig(is_emergency, stime, etime, is_platform=is_platform_maintenance)
        
        model_mgr.set_got_models([app_config])
        
        self.html_param['is_maintenance'] = app_config.is_maintenance()
        
        # 完了.
        self.putAlertToHtmlParam(u'メンテナンス設定を更新しました')
    
    def _proc_set_preregist_config(self):
        """事前登録の設定.
        """
        str_prizes = self.request.get('_prizes')
        etime = DateTimeUtil.strToDateTime(self.request.get('_etime'))
        
        try:
            prizes = Json.decode(str_prizes)
            if not isinstance(prizes, list) or not prizes:
                raise CabaretError()
        except:
            self.putAlertToHtmlParam(u'報酬はJson形式の配列で指定してください.例)[1,2]', alert_code=AlertCode.ERROR)
            return
        
        model_mgr = self.getModelMgr()
        prizes = list(set(prizes))
        prizelist = BackendApi.get_prizelist(model_mgr, prizes, using=settings.DB_READONLY)
        if len(prizelist) != len(prizes):
            self.putAlertToHtmlParam(u'報酬が存在しません', alert_code=AlertCode.ERROR)
            return
        
        def tr():
            model_mgr = ModelRequestMgr()
            config = BackendApi.get_preregistconfig(model_mgr)
            config.prizes = prizes
            config.etime = etime
            model_mgr.set_save(config)
            model_mgr.write_all()
            return model_mgr, config
        tmp_model_mgr, config = db_util.run_in_transaction(tr)
        tmp_model_mgr.write_end()
        
        model_mgr.set_got_models([config])
        
        # 完了.
        self.putAlertToHtmlParam(u'事前登録設定を更新しました')

    def _proc_set_cabaclubrankevent_config(self):
        """経営イベントの設定."""
        if SubProcessPid.exists(Defines.CLOSE_EVENT_PROCESS_NAME):
            self.putAlertToHtmlParam(u'イベント終了処理中は変更できません', AlertCode.ERROR)
            return

        mid = int(self.request.get('_cabaclubrankevent_mid') or 0)
        str_stime = self.request.get('_cabaclubrankevent_start')
        str_etime = self.request.get('_cabaclubrankevent_end')
        str_next_stime = self.request.get('_cabaclubrankevent_next_start')
        str_next_etime = self.request.get('_cabaclubrankevent_next_end')

        def WeekNumberToDateTime(str_time):
            # YYYYWW -> 週初
            year = str_time[:4]
            week_number = int(str_time[4:])

            # year/01/01
            basetime = datetime.datetime.strptime(year, '%Y').replace(tzinfo=timezone.TZ_DEFAULT)
            week_begin = (basetime + datetime.timedelta(days=(7*week_number))) - datetime.timedelta(days=basetime.weekday())
            return week_begin + datetime.timedelta(hours=Defines.CABARETCLUB_EVENT_DATE_CHANGE_TIME)

        stime = WeekNumberToDateTime(str_stime)
        etime = WeekNumberToDateTime(str_etime)
        next_stime = WeekNumberToDateTime(str_next_stime)
        next_etime = WeekNumberToDateTime(str_next_etime)

        model_mgr = self.getModelMgr()

        master = BackendApi.get_cabaclubrankeventmaster(model_mgr, mid, using=settings.DB_READONLY)
        if master is None:
            self.putAlertToHtmlParam(u'存在しないイベントです', AlertCode.ERROR)
            return

        args = (
            mid,
            stime,
            etime,
            next_stime,
            next_etime,
        )

        config = BackendApi.update_cabaclubrankeventconfig(*args)

        model_mgr.set_got_models([config])

        self.putAlertToHtmlParam(u'経営イベントを更新しました')

    def _proc_set_produceevent_config(self):
        """プロデュースイベントの設定.
        """
        print '_proc_set_produceevent_config'
        mid = int(self.request.get('_produceevent_mid') or 0)
        str_stime = self.request.get('_produceevent_start')
        str_etime = self.request.get('_produceevent_end')
        str_bigtime = self.request.get('_produceevent_bigtime')
        str_epilogue_endtime = self.request.get('_produceevent_epilogue_endtime')
        
        model_mgr = self.getModelMgr()

        master = BackendApi.get_produce_event_master(model_mgr, mid, using=settings.DB_DEFAULT)
        if master is None:
            self.putAlertToHtmlParam(u'存在しないイベントです', AlertCode.ERROR)
            return

        stime = DateTimeUtil.strToDateTime(str_stime)
        etime = DateTimeUtil.strToDateTime(str_etime)
        bigtime = DateTimeUtil.strToDateTime(str_bigtime)
        epilogue_endtime = DateTimeUtil.strToDateTime(str_epilogue_endtime)
        
        config = BackendApi.update_produce_event_config(mid, stime, etime, bigtime, epilogue_endtime)

        model_mgr.set_got_models([config])

        # 完了.
        self.putAlertToHtmlParam(u'プロデュースイベント設定を更新しました')
        
    def _proc_close_produceevent(self):
        """プロデュースイベント終了処理.
        """
#        cmd = CommandUtil.makeCommandString('python2.7', ['manage.py', 'close_produceevent'], workdir=Defines.PROJECT_DIR)
#        logtext = CommandUtil.execute([cmd], log=True)
        cmd = CommandUtil.makeCommandString('python2.7' if settings_sub.IS_LOCAL else '/usr/local/bin/python2.7', ['manage.py', 'close_produceevent'], workdir=Defines.PROJECT_DIR)
        logtext = CommandUtil.execute([cmd], log=True)
        
        self.response.send(logtext)
        
    def _proc_get_close_produceevent_log(self):
        """レイドイベント終了処理のチェック.
        """
        procname = Defines.CLOSE_EVENT_PRODUCE_NAME
        if SubProcessPid.exists(procname):
            self.response.send('runnning')
        else:
            # 前回の実行結果.
            def read(path):
                if not os.path.exists(path):
                    return u''
                f = None
                try:
                    f = open(path, 'r')
                except:
                    if f:
                        f.close()
                        f = None
                    return 'failed to open..%s' % path
            result = {
                'log':read(os.path.join(settings_sub.TMP_DOC_ROOT, '%s' % procname)),
                'err':read(os.path.join(settings_sub.TMP_DOC_ROOT, '%s_err' % procname)),
            }
            self.response.send(Json.encode(result))

    def _proc_set_raidevent_config(self):
        """レイドイベントの設定.
        """
        if SubProcessPid.exists(Defines.CLOSE_EVENT_PROCESS_NAME):
            self.putAlertToHtmlParam(u'イベント終了処理中は変更できません', AlertCode.ERROR)
            return
        
        mid = int(self.request.get('_raidevent_mid') or 0)
        str_stime = self.request.get('_raidevent_start')
        str_etime = self.request.get('_raidevent_end')
        str_bigtime = self.request.get('_raidevent_bigtime')
        str_ticket_endtime = self.request.get('_raidevent_ticketend')
        str_timebonus_time = self.request.get('_raidevent_timebonus_time')
        str_epilogue_endtime = self.request.get('_raidevent_epilogue_endtime')
        
        str_combobonus_opentime = self.request.get('_raidevent_combobonus_opentime')
        str_feverchance_opentime = self.request.get('_raidevent_feverchance_opentime')
        str_fastbonus_opentime = self.request.get('_raidevent_fastbonus_opentime')
        
        def checkTimeTable(name, timetable):
            if not timetable:
                return True
            
            if not isinstance(timetable, list):
                self.putAlertToHtmlParam(u'%s設定が不正です' % name, AlertCode.ERROR)
                return False
            
            for data in timetable:
                if not isinstance(data, dict):
                    self.putAlertToHtmlParam(u'%s設定に想定外のデータが含まれています' % name, AlertCode.ERROR)
                    return False
                
                diff = set(['stime','etime']) - set(data.keys())
                if diff:
                    self.putAlertToHtmlParam(u'%s設定に想定外のデータが含まれています' % name, AlertCode.ERROR)
                    return False
                elif not isinstance(data['stime'], datetime.datetime) or not isinstance(data['etime'], datetime.datetime):
                    self.putAlertToHtmlParam(u'%s時間に時間ではないデータが含まれています' % name, AlertCode.ERROR)
                    return False
            return True
        
        timebonus_time = Json.decode(str_timebonus_time) if str_timebonus_time else ''
        combobonus_opentime = Json.decode(str_combobonus_opentime) if str_combobonus_opentime else ''
        feverchance_opentime = Json.decode(str_feverchance_opentime) if str_feverchance_opentime else ''
        fastbonus_opentime = Json.decode(str_fastbonus_opentime) if str_fastbonus_opentime else ''
        
        if not checkTimeTable(u'タイムボーナス', timebonus_time):
            return
        elif not checkTimeTable(u'コンボボーナス', combobonus_opentime):
            return
        elif not checkTimeTable(u'フィーバーチャンス', feverchance_opentime):
            return
        elif not checkTimeTable(u'秘宝ボーナス', fastbonus_opentime):
            return
        
        # 追加ステージ.
        datalist = self.get_eventadditionalstage_requestdata('raideventadditionalstage')
        
        model_mgr = self.getModelMgr()
        
        master = BackendApi.get_raideventmaster(model_mgr, mid, using=settings.DB_DEFAULT)
        if master is None:
            self.putAlertToHtmlParam(u'存在しないイベントです', AlertCode.ERROR)
            return

        def _check_time(times):
            for time in times:
                if datetime.timedelta(0) < time['stime'] - time['etime']:
                    return False
            return True

        def _put_error_message(bonustype):
            self.putAlertToHtmlParam(u'{}終了時間が開始時間よりも早い時間に設定されています'.format(bonustype), AlertCode.ERROR)

        check_list = [
            (timebonus_time, u'タイムボーナス'),
            (combobonus_opentime, u'コンボボーナス'),
            (feverchance_opentime, u'フィーバーチャンス'),
            (fastbonus_opentime, u'秘宝ボーナス')
        ]

        for times, bonustype in check_list:
            if not _check_time(times):
                _put_error_message(bonustype)
                return

        args = (
            mid,
            DateTimeUtil.strToDateTime(str_stime),
            DateTimeUtil.strToDateTime(str_etime),
            DateTimeUtil.strToDateTime(str_bigtime),
            DateTimeUtil.strToDateTime(str_ticket_endtime),
            timebonus_time, combobonus_opentime, feverchance_opentime, fastbonus_opentime,
            DateTimeUtil.strToDateTime(str_epilogue_endtime),
            datalist
        )
        config = BackendApi.update_raideventconfig(*args)
        
        model_mgr.set_got_models([config])
        
        # 完了.
        self.putAlertToHtmlParam(u'レイドイベント設定を更新しました')
    
    def _proc_close_raidevent(self):
        """レイドイベント終了処理.
        """
#        procname = Defines.CLOSE_EVENT_PROCESS_NAME
#        if SubProcessPid.exists(procname):
#            self.response.send(u'終了処理実行中です')
#        else:
#            # プロセスを新規作成.
#            cmd = CommandUtil.makeCommandString('python2.7', ['manage.py', 'close_raidevent'])
##            cmd = ('python2.7', '--version')
#            
#            # ログ.
#            logfile = file(os.path.join(settings_sub.TMP_DOC_ROOT, '%s' % procname), "w")
#            errfile = file(os.path.join(settings_sub.TMP_DOC_ROOT, '%s_err' % procname), "w")
#            p = subprocess.Popen(cmd, stdout=logfile, stderr=errfile, env=os.environ, cwd=Defines.PROJECT_DIR)
#            SubProcessPid.create(procname, p.pid)
#            
#            p.wait()
#            
#            self.response.send(u'終了処理を開始しました')
        cmd = CommandUtil.makeCommandString('python2.7', ['manage.py', 'close_raidevent'], workdir=Defines.PROJECT_DIR)
        logtext = CommandUtil.execute([cmd], log=True)
        self.response.send(logtext)
    
    def _proc_get_close_raidevent_log(self):
        """レイドイベント終了処理のチェック.
        """
        procname = Defines.CLOSE_EVENT_PROCESS_NAME
        if SubProcessPid.exists(procname):
            self.response.send('runnning')
        else:
            # 前回の実行結果.
            def read(path):
                if not os.path.exists(path):
                    return u''
                f = None
                try:
                    f = open(path, 'r')
                except:
                    if f:
                        f.close()
                        f = None
                    return 'failed to open..%s' % path
            result = {
                'log':read(os.path.join(settings_sub.TMP_DOC_ROOT, '%s' % procname)),
                'err':read(os.path.join(settings_sub.TMP_DOC_ROOT, '%s_err' % procname)),
            }
            self.response.send(Json.encode(result))
    
    def _proc_init_raidevent(self):
        """レイドイベントの初期化.
        """
        mid = int(self.request.get('_raidevent_mid') or 0)
        
        model_mgr = self.getModelMgr()
        
        master = BackendApi.get_raideventmaster(model_mgr, mid, using=settings.DB_DEFAULT)
        if master is None:
            self.putAlertToHtmlParam(u'存在しないイベントです', AlertCode.ERROR)
            return
        
        def tr():
            model_mgr = ModelRequestMgr()
            BackendApi.tr_init_raidevent(model_mgr, mid)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        # 完了.
        self.putAlertToHtmlParam(u'レイドイベントを初期化しました.ID=%d' % mid)
    
    def _proc_set_scoutevent_config(self):
        """スカウトイベントの設定.
        """
        if SubProcessPid.exists(Defines.CLOSE_SCOUTEVENT_PROCESS_NAME):
            self.putAlertToHtmlParam(u'イベント終了処理中は変更できません', AlertCode.ERROR)
            return
        
        mid = int(self.request.get('_scoutevent_mid') or 0)
        str_stime = self.request.get('_scoutevent_start')
        str_etime = self.request.get('_scoutevent_end')
        str_epilogue_endtime = self.request.get('_scoutevent_epetime')
        str_present_endtime = self.request.get('_scoutevent_presentetime')
        
        model_mgr = self.getModelMgr()
        
        master = BackendApi.get_scouteventmaster(model_mgr, mid, using=settings.DB_DEFAULT)
        if master is None:
            self.putAlertToHtmlParam(u'存在しないイベントです', AlertCode.ERROR)
            return
        
        # 追加ステージ.
        datalist = self.get_eventadditionalstage_requestdata('scouteventadditionalstage')
        
        epilogue_endtime = DateTimeUtil.strToDateTime(str_epilogue_endtime)
        present_endtime = DateTimeUtil.strToDateTime(str_present_endtime)
        config = BackendApi.update_scouteventconfig(mid, DateTimeUtil.strToDateTime(str_stime), DateTimeUtil.strToDateTime(str_etime), epilogue_endtime=epilogue_endtime, stageschedule=datalist, present_endtime=present_endtime)
        
        model_mgr.set_got_models([config])
        
        # 完了.
        self.putAlertToHtmlParam(u'スカウトイベント設定を更新しました')
    
    def _proc_close_scoutevent(self):
        """スカウトイベント終了処理.
        """
#        cmd = CommandUtil.makeCommandString('python2.7', ['manage.py', 'close_raidevent'], workdir=Defines.PROJECT_DIR)
#        logtext = CommandUtil.execute([cmd], log=True)
        logtext = '未実装です'
        self.response.send(logtext)
    
    def _proc_get_close_scoutevent_log(self):
        """スカウトイベント終了処理のチェック.
        """
        procname = Defines.CLOSE_SCOUTEVENT_PROCESS_NAME
        if SubProcessPid.exists(procname):
            self.response.send('runnning')
        else:
            # 前回の実行結果.
            def read(path):
                if not os.path.exists(path):
                    return u''
                f = None
                try:
                    f = open(path, 'r')
                except:
                    if f:
                        f.close()
                        f = None
                    return 'failed to open..%s' % path
            result = {
                'log':read(os.path.join(settings_sub.TMP_DOC_ROOT, '%s' % procname)),
                'err':read(os.path.join(settings_sub.TMP_DOC_ROOT, '%s_err' % procname)),
            }
            self.response.send(Json.encode(result))
    
    def _proc_set_battleevent_config(self):
        """バトルイベントの設定.
        """
        mid = int(self.request.get('_battleevent_mid') or 0)
        str_stime = self.request.get('_battleevent_start')
        str_etime = self.request.get('_battleevent_end')
        is_emergency = bool(int(self.request.get('_is_emergency') or 0))
        str_ependtime = self.request.get('_battleevent_epend')
        str_ticketendtime = self.request.get('_battleevent_ticketend')
        
        model_mgr = self.getModelMgr()
        
        master = BackendApi.get_battleevent_master(model_mgr, mid, using=settings.DB_DEFAULT)
        if master is None:
            self.putAlertToHtmlParam(u'存在しないイベントです', AlertCode.ERROR)
            return
        
        # 追加ランク.
        cnt_max = int(self.request.get('cnt_max') or 0)
        ranklist = []
        datalist = []
        for cnt in xrange(cnt_max):
            rank = int(self.request.get('_battleeventadditionalrank_rank_%s' % cnt) or 0)
            if 0 < rank:
                if rank in ranklist:
                    self.putAlertToHtmlParam(u'ランクが重複しています', AlertCode.ERROR)
                    return
                
                ranklist.append(rank)
                
                str_time = self.request.get('_battleeventadditionalrank_start_%s' % cnt)
                datalist.append({
                    'rank' : rank,
                    'time' : DateTimeUtil.strToDateTime(str_time),
                })
        datalist.sort(key=lambda x:x['time'])
        rank = None
        for data in datalist:
            if rank is not None and data['rank'] < rank:
                self.putAlertToHtmlParam(u'ランクの公開スケジュールが不正です', AlertCode.ERROR)
                return
            rank = data['rank']
        
        stime = DateTimeUtil.strToDateTime(str_stime)
        etime = DateTimeUtil.strToDateTime(str_etime)
        ependtime = DateTimeUtil.strToDateTime(str_ependtime)
        ticketendtime = DateTimeUtil.strToDateTime(str_ticketendtime)
        config = BackendApi.update_battleeventconfig(mid, stime, etime, ependtime,ticketendtime, is_emergency=is_emergency, rankschedule=datalist)
        
        model_mgr.set_got_models([config])
        
        # 完了.
        self.putAlertToHtmlParam(u'バトルイベント設定を更新しました')
    
    def _proc_preparation_battleevent(self):
        """バトルイベント開始処理.
        """
        cmd = CommandUtil.makeCommandString('python2.7', ['manage.py', 'battleevent_preparation'], workdir=Defines.PROJECT_DIR)
        logtext = CommandUtil.execute([cmd], log=True)
        DbgLogger.write_app_log('battleevent_preparation', logtext)
        logtext = logtext.replace('\n', '<br />')
        self.putAlertToHtmlParam(u'バトルイベント開始処理が終了しました:<br />%s' % logtext)
    
    def _proc_aggregate_battleevent(self):
        """バトルイベント集計処理.
        """
        cmd = CommandUtil.makeCommandString('python2.7', ['manage.py', 'battleevent_aggregate'], workdir=Defines.PROJECT_DIR)
        logtext = CommandUtil.execute([cmd], log=True)
        DbgLogger.write_app_log('battleevent_aggregate', logtext)
        logtext = logtext.replace('\n', '<br />')
        self.putAlertToHtmlParam(u'バトルイベント集計処理が終了しました:<br />%s' % logtext)
    
    def _proc_close_battleevent(self):
        """バトルイベント終了処理.
        """
        cmd = CommandUtil.makeCommandString('python2.7', ['manage.py', 'close_battleevent'], workdir=Defines.PROJECT_DIR)
        logtext = CommandUtil.execute([cmd], log=True)
        DbgLogger.write_app_log('close_battleevent', logtext)
        logtext = logtext.replace('\n', '<br />')
        self.putAlertToHtmlParam(u'バトルイベント終了処理が終了しました:<br />%s' % logtext)
    
    def _proc_send_battleevent_grouprankprizes(self):
        """未受け取りのバトルイベントグループ別ランキング報酬を配布.
        """
        model_mgr = self.getModelMgr()
        master = BackendApi.get_current_battleevent_master(model_mgr)
        if master is None:
            self.putAlertToHtmlParam(u'イベントが設定されていません', AlertCode.ERROR)
            return
        
        num = BackendApi.battleevent_send_groupranking_prizes(master)
        
        # 完了.
        if 0 < num:
            self.putAlertToHtmlParam(u'未受け取りのバトルイベントグループ別ランキング報酬を配布しました.%s' % num)
        else:
            self.putAlertToHtmlParam(u'未受け取りのバトルイベントグループ別ランキング報酬がありませんでした')
    
    def _proc_set_totalloginbonus_config(self):
        """累計ログインボーナスの設定.
        """
        mid = int(self.request.get('_totalloginbonus_mid') or 0)
        str_stime = self.request.get('_totalloginbonus_start')
        str_etime = self.request.get('_totalloginbonus_end')
        mid_next = int(self.request.get('_totalloginbonus_mid_next') or 0)
        continuity_login = self.request.get('_continuity_login') == "1"
        
        
        model_mgr = self.getModelMgr()
        
        def checkMaster(masterid):
            master = BackendApi.get_loginbonustimelimitedmaster(model_mgr, masterid, using=settings.DB_READONLY)
            if master is None:
                self.putAlertToHtmlParam(u'存在しないログインボーナスです.ID=%s' % masterid, AlertCode.ERROR)
                return False
            
            table = BackendApi.get_loginbonustimelimiteddaysmaster_day_table_by_timelimitedmid(model_mgr, masterid, using=settings.DB_READONLY)
            if not table:
                self.putAlertToHtmlParam(u'ログインボーナスに報酬が設定されていません.ID=%s' % masterid, AlertCode.ERROR)
                return False
                
            days = table.keys()
            days.sort()
            if days[0] != 1 or days[-1] != len(days):
                self.putAlertToHtmlParam(u'ログインボーナスの報酬の日数に抜けがあります.ID=%s' % masterid, AlertCode.ERROR)
                return False
            
            return True
        
        if mid_next and not checkMaster(mid_next):
            return
        elif not checkMaster(mid):
            return
        
        stime = DateTimeUtil.strToDateTime(str_stime)
        etime = DateTimeUtil.strToDateTime(str_etime)
        config = BackendApi.update_totalloginbonusconfig(model_mgr, mid, stime, etime, mid_next, continuity_login)
        
        model_mgr.set_got_models([config])
        
        # 完了.
        self.putAlertToHtmlParam(u'累計ログインボーナス設定を更新しました')
    
    def _proc_set_loginbonustimelimited_config(self):
        """期間付ログインボーナスの設定.
        """
        LOGINBONUS_MODELS = dict(login=LoginBonusTimeLimitedMaster, sugoroku=LoginBonusSugorokuMaster)
        
        cnt_max = int(self.request.get('cnt_max') or 0)
        
        model_mgr = self.getModelMgr()
        
        datalist = []
        valuelist = []
        for cnt in xrange(cnt_max):
            value = self.request.get('_loginbonustimelimited_mid_%s' % cnt)
            if not value:
                continue
            arr = value.split(',')
            if len(arr) != 2:
                continue
            elif arr[0] not in LOGINBONUS_MODELS:
                continue
            
            if value in valuelist:
                self.putAlertToHtmlParam(u'ロングログインボーナスが重複しています', AlertCode.ERROR)
                return
            
            model_name = arr[0]
            model_cls = LOGINBONUS_MODELS[model_name]
            mid = int(arr[1])
            
            master = model_mgr.get_model(model_cls, mid, using=settings.DB_READONLY)
            if master is None:
                self.putAlertToHtmlParam(u'存在しないロングログインボーナスです', AlertCode.ERROR)
                return
            valuelist.append(value)
            
            str_stime = self.request.get('_loginbonustimelimited_start_%s' % cnt)
            str_etime = self.request.get('_loginbonustimelimited_end_%s' % cnt)
            beginer = self.request.get('_loginbonustimelimited_beginer_%s' % cnt) == '1'
            datalist.append({
                'mid' : mid,
                'stime' : DateTimeUtil.strToDateTime(str_stime),
                'etime' : DateTimeUtil.strToDateTime(str_etime),
                'beginer' : beginer,
                'sugoroku' : model_name == 'sugoroku',
            })
        
        config = BackendApi.update_loginbonustimelimitedconfig(model_mgr, datalist)
        model_mgr.set_got_models([config])
        
        # 完了.
        self.putAlertToHtmlParam(u'ロングログインボーナス設定を更新しました')
    
    def _proc_set_comebackcampaign_config(self):
        """カムバックキャンペーンの設定.
        """
        cnt_max = int(self.request.get('cnt_max') or 0)
        
        model_mgr = self.getModelMgr()
        
        datalist = []
        midlist = []
        for cnt in xrange(cnt_max):
            mid = int(self.request.get('_comebackcampaign_mid_%s' % cnt) or 0)
            
            if mid:
                if mid in midlist:
                    self.putAlertToHtmlParam(u'カムバックキャンペーンが重複しています', AlertCode.ERROR)
                    return
                
                master = BackendApi.get_comebackcampaignmaster(model_mgr, mid, using=settings.DB_READONLY)
                if master is None:
                    self.putAlertToHtmlParam(u'存在しないカムバックキャンペーンです', AlertCode.ERROR)
                    return
                midlist.append(mid)
                
                str_stime = self.request.get('_comebackcampaign_start_%s' % cnt)
                str_etime = self.request.get('_comebackcampaign_end_%s' % cnt)
                datalist.append({
                    'mid' : mid,
                    'stime' : DateTimeUtil.strToDateTime(str_stime),
                    'etime' : DateTimeUtil.strToDateTime(str_etime),
                })
        
        config = BackendApi.update_comebackcampaignconfig(model_mgr, datalist)
        model_mgr.set_got_models([config])
        
        # 完了.
        self.putAlertToHtmlParam(u'カムバックキャンペーン設定を更新しました')
    
    def _proc_reset_raiddestroycount(self):
        """レイドの討伐回数をリセット.
        """
        def tr():
            model_mgr = ModelRequestMgr()
            BackendApi.tr_reset_raid_destroyrecord(model_mgr)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        # 完了.
        self.putAlertToHtmlParam(u'レイド討伐回数を0にしました.')
    
    def _proc_flush_cache(self):
        """キャッシュのクリア.
        """
        rediscache.flush_all()
        self.putAlertToHtmlParam(u'キャッシュを全て削除しました')
    
    def _proc_flush_session(self):
        """セッションのクリア.
        """
        client = OSAUtil.get_session_client()
        client.flush()
        self.putAlertToHtmlParam(u'セッションを全て削除しました')
    
    def _proc_flush_lastview_area(self):
        """最後に見たエリアをクリア.
        """
        LastViewArea.getDB().delete(LastViewArea.KEY)
        self.putAlertToHtmlParam(u'最後に見たエリアを全て削除しました')
    
    def __get_present_message_id(self):
        """プレゼントに付与するメッセージのID.
        """
        message_id = self.request.get('_message_id') or 0
        if message_id:
            try:
                message_id = int(message_id)
            except:
                self.putAlertToHtmlParam(u'テキストIDが不正です.' , alert_code=AlertCode.ERROR)
                return None
        else:
            message_id = 0
            message = self.request.get('_message')
            if message:
                def tr():
                    idmax = TextMaster.all().aggregate(Max('id')).get('id__max')
                    model_mgr = ModelRequestMgr()
                    ins = TextMaster()
                    ins.id = max(Defines.TextMasterID.AUTO_CREATION_ID_MIN, idmax + 1)
                    ins.text = message
                    model_mgr.set_save(ins)
                    
                    def writeEnd():
                        model_mgr.get_mastermodel_all(TextMaster, fetch_deleted=True, using=settings.DB_DEFAULT, reflesh=True)
                    model_mgr.add_write_end_method(writeEnd)
                    model_mgr.write_all()
                    
                    return model_mgr, ins
                tmp_model_mgr, ins = db_util.run_in_transaction(tr)
                tmp_model_mgr.write_end()
                message_id = ins.id
        return message_id
    
    def __get_present_prizedata(self):
        """プレゼントの内容.
        """
        value = self.request.get('_value')
        
        # 種別.
        try:
            itype = int(self.request.get('_itype'))
            if not Defines.ItemType.PRESENT_TYPES.has_key(itype):
                raise CabaretError()
        except:
            self.putAlertToHtmlParam(u'不正なアイテムタイプです.' , alert_code=AlertCode.ERROR)
            return
        
        # 個数.
        try:
            inum = int(self.request.get('_num', '1'))
            if inum < 1:
                raise CabaretError()
        except:
            self.putAlertToHtmlParam(u'個数は自然数で入力してください.' , alert_code=AlertCode.ERROR)
            return None
        
        if itype == Defines.ItemType.CARD:
            master = BackendApi.get_cardmasters([int(value)], using=settings.DB_READONLY).get(int(value), None)
            if master is None:
                return None
            prize = PrizeData.create(cardid=master.id, cardnum=inum)
        elif itype == Defines.ItemType.ITEM:
            master = BackendApi.get_itemmaster(self.getModelMgr(), int(value), using=settings.DB_READONLY)
            if master is None:
                return None
            prize = PrizeData.create(itemid=master.id, itemnum=inum)
        elif itype == Defines.ItemType.ADDITIONAL_GACHATICKET:
            prize = PrizeData.create(additional_ticket_id=int(value), additional_ticket_num=inum)
        elif itype in (Defines.ItemType.GOLD, Defines.ItemType.GACHA_PT, Defines.ItemType.RAREOVERTICKET, 
                     Defines.ItemType.MEMORIESTICKET, Defines.ItemType.TRYLUCKTICKET, Defines.ItemType.GACHATICKET):
            if not str(value).isdigit() or int(value) < 1:
                self.putAlertToHtmlParam(u'値が不正です.%s' % value, alert_code=AlertCode.ERROR)
                return None
            value = int(value)
            keys = {
                Defines.ItemType.GOLD : 'gold',
                Defines.ItemType.GACHA_PT : 'gachapt',
                Defines.ItemType.RAREOVERTICKET : 'rareoverticket',
                Defines.ItemType.MEMORIESTICKET : 'memoriesticket',
                Defines.ItemType.TRYLUCKTICKET : 'ticket',
                Defines.ItemType.GACHATICKET : 'gachaticket',
            }
            args = {
                keys[itype] : value
            }
            prize = PrizeData.create(**args)
        else:
            self.putAlertToHtmlParam(u'未対応のタイプです.%d' % itype, alert_code=AlertCode.ERROR)
            return None
        return prize

    def __get_present_prizedata_by_prizemaster(self, prize_id):
        """PrizeMasterからプレゼントの内容を決定する.
        """
        model_mgr = self.getModelMgr()
        master = model_mgr.get_model(PrizeMaster, prize_id, using=settings.DB_READONLY)
        if master is None:
            self.putAlertToHtmlPar('存在しないマスターデータです. id=%s' % prize_id, alert_code=AlertCode.ERROR)
            return None

        prize = PrizeData.createByMaster(master)
        return prize
    
    def _proc_send_present(self):
        """プレゼントを送信.
        """
        struid = self.request.get('_uid')
        
        # ユーザー.
        try:
            uid_list = list(set([int(s) for s in struid.split(',') if s]))
            playerlist = BackendApi.get_players(self, uid_list, [], using=settings.DB_READONLY, model_mgr=self.getModelMgr())
            if len(playerlist) != len(uid_list):
                raise CabaretError()
        except:
            self.putAlertToHtmlParam(u'存在しないユーザIDが含まれています.' , alert_code=AlertCode.ERROR)
            return
        if not uid_list:
            self.putAlertToHtmlParam(u'ユーザIDが指定されていません.' , alert_code=AlertCode.ERROR)
            return
        
        # メッセージ.
        message_id = self.__get_present_message_id()
        if message_id is None:
            return
        
        # 配布するもの.
        if self.request.get('_itype'):
            prize = self.__get_present_prizedata()
        else:
            try:
                prize_id = int(self.request.get('_prize_id'))
            except:
                self.putAlertToHtmlPara(u'指定したマスターIDが不正です. id=%s' % self.request.get('_prize_id'), alert_code=AlertCode.ERROR)
            prize = self.__get_present_prizedata_by_prizemaster(prize_id)

        if prize is None:
            return
        
        def tr_write(prizelist, textid):
            model_mgr = ModelRequestMgr()
            for uid in uid_list:
                BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr_write, [prize], message_id)
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'ユーザID:[%s]にプレゼントを送信しました.' % struid, alert_code=AlertCode.SUCCESS)
    
    def _proc_send_presenteveryone(self):
        """全プレを送信.
        """
        # テキストマスター.
        message_id = self.__get_present_message_id()
        if message_id is None:
            return
        
        # 配布するもの.
        prizedata = self.__get_present_prizedata()
        if prizedata is None:
            return
        
        # 期間.
        try:
            date_from = DateTimeUtil.strToDateTime(self.request.get('_date_from'), "%Y-%m-%d %H:%M")
            date_to = DateTimeUtil.strToDateTime(self.request.get('_date_to'), "%Y-%m-%d %H:%M")
        except:
            self.putAlertToHtmlParam(u'日付のフォーマットが不正です.yyyy-mm-dd hh:mmの形式で指定してください' , alert_code=AlertCode.ERROR)
            return
        
        # 管理用の名前.
        present_name = self.request.get('_present_name')
        
        now = OSAUtil.get_now()
        
        def tr(present_name, prizedata, message_id, date_from, date_to, now):
            model_mgr = ModelRequestMgr()
            
            def get_mid(master_cls):
                mid = master_cls.max_value('id', default_value=Defines.PRESENTEVERYONE_AUTO_CREATION_ID_MIN-1)
                return max(mid+1, Defines.PRESENTEVERYONE_AUTO_CREATION_ID_MIN)
            
            # 追加したマスターデータ情報.
            additional_mastername_list = []
            def set_save(master):
                model_mgr.set_save(master)
                additional_mastername_list.append(u'%s:%s' % (master.__class__.__name__, master.key()))
            
            # スケジュールマスター作成.
            mid = get_mid(ScheduleMaster)
            schedulemaster = ScheduleMaster.makeInstance(mid)
            schedulemaster.stime = date_from
            schedulemaster.etime = date_to
            schedulemaster.timelimit = 1440
            schedulemaster.target = range(10)
            set_save(schedulemaster)
            
            # 報酬マスター作成.
            prizemaster = prizedata.to_master()
            prizemaster.id = get_mid(PrizeMaster)
            set_save(prizemaster)
            
            # 全プレのマスター作成.
            mid = get_mid(PresentEveryoneMypageMaster)
            presentmaster = PresentEveryoneMypageMaster.makeInstance(mid)
            presentmaster.name = present_name or u'自動生成:%s' % mid
            presentmaster.prizes = [prizemaster.id]
            presentmaster.textid = message_id
            presentmaster.schedule = schedulemaster.id
            set_save(presentmaster)
            
            # 配布開始時間を過ぎているなら全プレ予約を更新.
            if date_from <= now < date_to:
                model = PresentEveryoneRecord.getInstanceByKey(DateTimeUtil.datetimeToDate(now, logintime=False))
                model.mid_mypage.append(presentmaster.id)
                model.mid_mypage = list(set(model.mid_mypage))
                set_save(model)
            
            def writeEnd():
                localcache.Client().flush()
            model_mgr.add_write_end_method(writeEnd)
            
            model_mgr.write_all()
            
            return model_mgr, additional_mastername_list
        model_mgr, additional_mastername_list = db_util.run_in_transaction(tr, present_name, prizedata, message_id, date_from, date_to, now)
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'全プレの設定を追加しました.<br />追加したもの:<br />　%s' % u'<br />　'.join(additional_mastername_list) , alert_code=AlertCode.SUCCESS)
    
    def _proc_save_infomation(self):
        """お知らせを設定.
        """
        model_mgr = self.getModelMgr()
        
        # ID.
        mid = int(self.request.get('_mid') or 0)
        if mid and BackendApi.get_infomation(model_mgr, mid, using=settings.DB_READONLY) is None:
            self.putAlertToHtmlParam(u'指定したお知らせのIDが見つかりませんでした', alert_code=AlertCode.ERROR)
            return
        
        # タイトル.
        title = self.request.get('_title')
        if not title:
            self.putAlertToHtmlParam(u'タイトルが未設定です', alert_code=AlertCode.ERROR)
            return
        
        # 本文.
        body = self.request.get('_body')
        if not body:
            self.putAlertToHtmlParam(u'本文が未設定です', alert_code=AlertCode.ERROR)
            return
        
        # 掲載開始日.
        stime = None
        try:
            stime = DateTimeUtil.strToDateTime(self.request.get('_stime'), dtformat="%Y-%m-%d %H:%M")
        except:
            pass
        if stime is None:
            self.putAlertToHtmlParam(u'掲載開始時間が不正です。yyyy-mm-dd hh:mmの形式で入力してください', alert_code=AlertCode.ERROR)
            return
        
        # 掲載終了日.
        etime = None
        try:
            etime = DateTimeUtil.strToDateTime(self.request.get('_etime'), dtformat="%Y-%m-%d %H:%M")
        except:
            pass
        if etime is None:
            self.putAlertToHtmlParam(u'掲載終了時間が不正です。yyyy-mm-dd hh:mmの形式で入力してください', alert_code=AlertCode.ERROR)
            return
        
        def tr(mid, title, body, stime, etime):
            model_mgr = ModelRequestMgr()
            
            # マスターIDを探す.
            is_update = 0 < mid
            if not is_update:
                mid = InfomationMaster.max_value('id', default_value=Defines.INFOMATION_AUTO_CREATION_ID_MIN-1)
                mid = max(mid+1, Defines.INFOMATION_AUTO_CREATION_ID_MIN)
            
            # マスターデータを作成.
            ins = InfomationMaster.makeInstance(mid)
            ins.title = title
            ins.body = body
            ins.stime = stime
            ins.etime = etime
            model_mgr.set_save(ins)
            
            def writeEnd():
                if is_update:
                    localcache.Client().flush()
                redisdb = InfomationMasterIdListCache.getDB()
                redisdb.delete(InfomationMasterIdListCache.makeKey())
                ModelRequestMgr().get_mastermodel_all(InfomationMaster, fetch_deleted=True, reflesh=True)
            model_mgr.add_write_end_method(writeEnd)
            
            model_mgr.write_all()
            
            return model_mgr, is_update, mid
        model_mgr, is_update, mid = db_util.run_in_transaction(tr, mid, title, body, stime, etime)
        model_mgr.write_end()
        
        if is_update:
            self.putAlertToHtmlParam(u'お知らせ(ID:%s)を更新しました' % mid, alert_code=AlertCode.SUCCESS)
        else:
            self.putAlertToHtmlParam(u'お知らせ(ID:%s)を作成しました' % mid, alert_code=AlertCode.SUCCESS)
    
    def _proc_prev_infomation(self):
        """お知らせを設定.
        """
        # タイトル.
        title = self.request.get('_title') or ""
        
        # 本文.
        body = self.request.get('_body') or ""
        
        # 掲載開始日.
        stime = None
        try:
            stime = DateTimeUtil.strToDateTime(self.request.get('_stime'), dtformat="%Y-%m-%d %H:%M")
        except:
            stime = OSAUtil.get_now()
        
        # マスターデータを作成.
        ins = InfomationMaster.makeInstance(0)
        ins.title = title
        ins.body = body
        ins.stime = stime
        ins.etime = stime
        obj_infomation = Objects.infomation(self, ins)
        self.html_param['infomation'] = obj_infomation
        self.html_param['infomations'] = [obj_infomation]
        
        self.html_param['url_static_img'] = self.url_static + 'img/sp/large/'
        self.html_param['url_static_js'] = self.url_static + 'js/sp/'
        self.html_param['url_static_css'] = self.url_static + 'css/sp/'
        self.html_param['is_dev'] = False
        
        self.writeAppHtml('infomation_test')
    
    def _proc_add_messagerequest(self):
        """メッセージAPIのリクエストのキューを追加.
        """
        def checkString(name, text, maxlength):
            if not text:
                self.putAlertToHtmlParam(u'%sが入力されていません' % name, alert_code=AlertCode.ERROR)
                return False
            elif maxlength < StrUtil.getByteLength(text):
                self.putAlertToHtmlParam(u'%sが長過ぎます' % name, alert_code=AlertCode.ERROR)
                return False
            return True
        
        # タイトル.
        title = self.request.get('_title') or ""
        if not checkString(u'タイトル', title, 26):
            return
        
        # 本文.
        body = self.request.get('_body') or ""
        if not checkString(u'本文', body, 100):
            return
        
        # 送信時間.
        stime = None
        try:
            stime = DateTimeUtil.strToDateTime(self.request.get('_stime'), dtformat="%Y-%m-%d %H:%M")
        except:
            self.putAlertToHtmlParam(u'送信時間が不正です', alert_code=AlertCode.ERROR)
            return False
        
        # 飛び先.
        jumpto = self.request.get('_jumpto') or ""
        
        def tr(title, body, stime, jumpto):
            model_mgr = ModelRequestMgr()
            ins = MessageQueue()
            ins.title = title
            ins.body = body
            ins.stime = stime
            ins.jumpto = jumpto
            model_mgr.set_save(ins)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr, title, body, stime, jumpto).write_end()
        
        self.putAlertToHtmlParam(u'メッセージ送信予約を追加しました', alert_code=AlertCode.SUCCESS)
    
    def _proc_reset_tradestock(self):
        """現在公開中の秘宝交換の在庫をリセットする.
        """
        # リセット日.
        try:
            str_resettime = self.request.get('_resettime')
            if str_resettime == 'now':
                resettime = OSAUtil.get_now()
            else:
                resettime = DateTimeUtil.strToDateTime(self.request.get('_resettime'), dtformat="%Y-%m-%d %H:%M")
        except:
            self.putAlertToHtmlParam(u'リセット時間が不正です.yyyy-mm-dd HH:MMの形式で指定してください', alert_code=AlertCode.ERROR)
            return
        
        model_mgr = self.getModelMgr()
        self.html_param['trade_resettime'] = BackendApi.update_trade_resettime(model_mgr, resettime)
        
        self.putAlertToHtmlParam(u'秘宝交換の在庫リセット時間を変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_reflesh_redisdata(self):
        """redisのモデルを更新.
        やること多そうなので最低限のものだけ置いて随時追加.
        """
        pipe = RedisModel.getDB().pipeline()
        
        tasks = []
        model_mgr = self.getModelMgr()
        # 対戦相手選べるように.
        for level in xrange(BackendApi.get_playermaxlevel(model_mgr, using=settings.DB_READONLY)+1):
            for player in PlayerExp.fetchValues(['id'], filters={'level':level}, limit=100, using=settings.DB_READONLY):
                BackendApi.save_battle_levelset(player.id, level, pipe)
        tasks.append(u'・PVPの対戦相手検索を再設定')
        
        LIMIT = 1000
        player_num = Player.count()
        for i in xrange(int((player_num + LIMIT - 1) / LIMIT)):
            offset = i * LIMIT
            for p in Player.fetchValues(['id'], order_by='id', limit=LIMIT, offset=offset):
                BackendApi.preload_usercardidlist(model_mgr, p.id)
        tasks.append(u'・カードを設定')
        
        pipe.execute()
        
        self.putAlertToHtmlParam(u'以下の設定を行いました.<br />%s' % (u'<br />'.join(tasks)), alert_code=AlertCode.SUCCESS)
    
    def _proc_reset_popuptime(self):
        """ポップアップの閲覧状態をリセット.
        """
        BackendApi.update_popup_reset_time()
        self.putAlertToHtmlParam(u'ポップアップの閲覧フラグをリセットしました', alert_code=AlertCode.SUCCESS)
    
    #=======================================================
    def get_eventadditionalstage_requestdata(self, name):
        # 追加ステージ.
        cnt_max = int(self.request.get('cnt_max') or 0)
        stagelist = []
        datalist = []
        for cnt in xrange(cnt_max):
            stage = int(self.request.get('_{}_stage_{}'.format(name, cnt)) or 0)
            if 0 < stage:
                if stage in stagelist:
                    self.putAlertToHtmlParam(u'ステージが重複しています', AlertCode.ERROR)
                    return
                
                stagelist.append(stage)
                
                str_time = self.request.get('_{}_start_{}'.format(name, cnt))
                datalist.append({
                    'stage' : stage,
                    'time' : DateTimeUtil.strToDateTime(str_time),
                })
        datalist.sort(key=lambda x:x['time'])
        
        stage = None
        for data in datalist:
            if stage is not None and data['stage'] < stage:
                self.putAlertToHtmlParam(u'ステージの公開スケジュールが不正です', AlertCode.ERROR)
                return
            stage = data['stage']
        
        return datalist
    
def main(request):
    return Handler.run(request)
