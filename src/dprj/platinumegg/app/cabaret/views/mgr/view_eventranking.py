# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
import settings
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from defines import Defines
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Player import PlayerExp
from platinumegg.app.cabaret.util.alert import AlertCode
import settings_sub
import os
from platinumegg.app.cabaret.util.csvutil import CSVWriter
from platinumegg.app.cabaret.models.Gacha import GachaMaster
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
import datetime
from platinumegg.lib.platform.api.objects import People

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Handler(AdminHandler):
    """開催中のイベントのランキングを確認.
    """
    def process(self):
        
        # どのイベントか.
        target = self.request.get('_target')
        is_beginer = self.request.get('_beginer') == '1'
        self.__target = target
        self.__is_beginer = is_beginer
        self.html_param['_target'] = target
        self.html_param['_beginer'] = is_beginer
        
        func = getattr(self, '_proc_%s' % target, None)
        if func:
            func()
            if self.response.isEnd:
                return
        
        self.writeAppHtml('infomations/view_eventranking')
    
    def __get_csv(self, filename, ranker_num_getter, ranking_getter, specialgacha_masters):
        """csvを取得.
        """
        is_update = self.request.get('_update') == '1'
        if not os.path.exists(settings_sub.KPI_ROOT):
            os.mkdir(settings_sub.KPI_ROOT)
        
        dirpath = os.path.join(settings_sub.KPI_ROOT, 'eventranking')
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        
        filepath = os.path.join(dirpath, filename)
        
        if is_update:
            model_mgr = self.getModelMgr()
            writer = CSVWriter(filepath)
            writer.add([u'作成時間:%s' % OSAUtil.get_now().strftime("%Y/%m/%d %H:%M:%S")])
            
            offset = 0
            LIMIT = 300
            
            # タイトル.
            writer.add([u'順位', u'獲得ポイント', u'ユーザ名', u'ユーザID', u'DMMID', u'No.1キャスト', u'特効ガチャ課金額'])
            while True:
                # ユーザIDとスコアを取得.
                data_dict = dict(ranking_getter(offset, LIMIT))
                if not data_dict:
                    break
                
                uidlist = data_dict.keys()
                leaders = BackendApi.get_leaders(uidlist, model_mgr, using=backup_db)
                data_list = list(data_dict.items())
                data_list.sort(key=lambda x:x[1][1])
                
                for uid, data in data_list:
                    total_money = self.get_payment_money_for_gachamasters(uid, specialgacha_masters)
                    score, rank = data
                    leader = leaders[uid]
                    player = BackendApi.get_player(self, uid, using=backup_db)
                    person = BackendApi.get_dmmplayers(self, [player], using=backup_db)[player.dmmid]
                    nickname = person.nickname
                    dmmid = player.dmmid
                    
                    writer.add([rank, score, nickname, uid, dmmid, u'%s(ID:%s)' % (leader.master.name, leader.master.id), total_money])
                
                offset += LIMIT
            
            writer.output()
            return None
        
        csv_data = None
        f = None
        try:
            f = open(filepath, 'rb')
            csv_data = f.read()
            f.close()
        except:
            if f:
                f.close()
            raise
        
        return csv_data

    def get_payment_money_for_gachamasters(self, uid, gacha_masters):
        total_money = 0
        paymentlist = BackendApi.get_gachapaymententry_list(uid, True, using=backup_db)

        for gacha_master in gacha_masters:
            total_money += sum(x.price for x in paymentlist if x.iid==gacha_master.id)
        return total_money

    def __put_csvurl(self, target, eventmaster):
        filename = u'%s.csv' % eventmaster.codename
        filepath = os.path.join(settings_sub.KPI_ROOT, 'eventranking', filename)
        
        url = UrlMaker.view_eventranking()
        url = OSAUtil.addQuery(url, '_target', target)
        url = OSAUtil.addQuery(url, '_beginer', '1' if self.__is_beginer else '0')
        if os.path.exists(filepath):
            self.html_param['url_csv'] = self.makeAppLinkUrlAdmin(url)
        self.html_param['url_csv_update'] = self.makeAppLinkUrlAdmin(OSAUtil.addQuery(url, '_update', '1'))
    
    def __put_ranking(self, ranker_num_getter, ranking_getter, special_gachamasters):
        """ランキング情報を埋め込む.
        """
        CONTENT_NUM_PER_PAGE = 100
        
        model_mgr = self.getModelMgr()
        
        # 表示するページ.
        page = self.request.get(Defines.URLQUERY_PAGE)
        if page and page.isdigit():
            page = int(page)
        else:
            page = 0
        
        # ランキングにいる人数.
        ranker_num = ranker_num_getter()
        
        # ユーザIDとスコアを取得.
        offset = page * CONTENT_NUM_PER_PAGE
        data_dict = dict(ranking_getter(offset, CONTENT_NUM_PER_PAGE))
        
        # プレイヤー情報.
        uidlist = data_dict.keys()
        playerlist = BackendApi.get_players(self, uidlist, [PlayerExp], using=backup_db, model_mgr=model_mgr)
        persons = BackendApi.get_dmmplayers(self, playerlist, using=backup_db)
        leaders = BackendApi.get_leaders(uidlist, model_mgr, using=backup_db)
        obj_playerlist = []
        for player in playerlist:
            total_money = self.get_payment_money_for_gachamasters(player.id, special_gachamasters)
            obj_player = Objects.player(self, player, persons[player.dmmid], leaders.get(player.id))
            score, rank = data_dict[player.id]
            obj_player.update({
                'rank' : rank,
                'score' : score,
                'url' : self.makeAppLinkUrlAdmin(UrlMaker.view_player(player.id)),
                'total_money' : total_money
            })
            obj_playerlist.append(obj_player)
        if not obj_playerlist:
            self.putAlertToHtmlParam(u'ランキングデータがありません', alert_code=AlertCode.WARNING)
        
        obj_playerlist.sort(key=lambda x:x['rank'])
        self.html_param['playerlist'] = obj_playerlist
        
        # ページング.
        url = UrlMaker.view_eventranking()
        url = OSAUtil.addQuery(url, '_target', self.__target)
        url = OSAUtil.addQuery(url, '_beginer', self.__is_beginer)
        self.putPagenation(url, page, ranker_num, CONTENT_NUM_PER_PAGE)

        # ガチャ情報
        self.html_param['special_gachamasters'] = special_gachamasters
        
    def _proc_raid(self):
        """レイドイベント.
        """
        model_mgr = self.getModelMgr()
        
        # 対象のレイドイベント.
        config = BackendApi.get_current_raideventconfig(model_mgr, using=backup_db)
        eventid = config.mid
        
        # ランキング情報埋め込み.
        special_gachamasters = self.get_special_gachamaster(model_mgr, [8], config.starttime, config.endtime)
        ranker_num_getter = lambda : BackendApi.get_raidevent_rankernum(eventid, self.__is_beginer)
        ranking_getter = lambda offset,limit : BackendApi.fetch_uid_by_raideventrank(eventid, limit, offset, True, self.__is_beginer)
        self.__put_ranking(ranker_num_getter, ranking_getter, special_gachamasters)
        
        eventmaster = BackendApi.get_raideventmaster(model_mgr, eventid, using=backup_db)
        self.__put_csvurl('makeraidcsv', eventmaster)
    
    def _proc_makeraidcsv(self):
        model_mgr = self.getModelMgr()
        
        # 対象のレイドイベント.
        config = BackendApi.get_current_raideventconfig(model_mgr, using=backup_db)
        eventid = config.mid
        eventmaster = BackendApi.get_raideventmaster(model_mgr, eventid, using=backup_db)
        
        # CSV作成.
        filename = u'%s.csv' % eventmaster.codename
        
        special_gachamasters = self.get_special_gachamaster(model_mgr, [8], config.starttime, config.endtime)
        ranker_num_getter = lambda : BackendApi.get_raidevent_rankernum(eventid, self.__is_beginer)
        ranking_getter = lambda offset,limit : BackendApi.fetch_uid_by_raideventrank(eventid, limit, offset, True, self.__is_beginer)
        
        csv_data = self.__get_csv(filename, ranker_num_getter, ranking_getter, special_gachamasters)
        
        if csv_data:
            self.osa_util.write_csv_data(csv_data, filename)
        else:
            self._proc_raid()

    def get_special_gachamaster(self, model_mgr, special_gacha_consumetypes, search_start_time, search_end_time):
        #特定のコンシュームタイプで、ガチャのスケージュールが特定の期間ならそれは特効ガチャのはず。
        gachamaster_list = GachaMaster.fetchValues(filters=({'consumetype__in':special_gacha_consumetypes}), using=backup_db)

        special_gachamasters = []
        for gachamaster in gachamaster_list:
            schedule_master = model_mgr.get_model(ScheduleMaster, gachamaster.schedule)
            if search_start_time.date() <= schedule_master.stime.date() and schedule_master.etime.date() <= search_end_time.date():
                special_gachamasters.append(gachamaster)
        
        if special_gachamasters:
            return special_gachamasters
        else:
            self.putAlertToHtmlParam(u'特効ガチャが見つけられませんでした', AlertCode.INFO)
            return None

    def _proc_scout(self):
        """スカウトイベント.
        """
        model_mgr = self.getModelMgr()
        
        # 対象のスカウトイベント.
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=backup_db)
        eventid = config.mid
        
        # ランキング情報埋め込み.
        special_gachas = self.get_special_gachamaster(model_mgr, [9, 48], config.starttime - datetime.timedelta(days=1), config.endtime)
        ranker_num_getter = lambda : BackendApi.get_scoutevent_rankernum(eventid, self.__is_beginer)
        ranking_getter = lambda offset,limit : BackendApi.fetch_uid_by_scouteventrank(eventid, limit, offset, True, self.__is_beginer)
        
        self.__put_ranking(ranker_num_getter, ranking_getter, special_gachas)
        
        eventmaster = BackendApi.get_scouteventmaster(model_mgr, eventid, using=backup_db)
        self.__put_csvurl('makescoutcsv', eventmaster)
    
    def _proc_makescoutcsv(self):
        model_mgr = self.getModelMgr()
        
        # 対象のスカウトイベント.
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=backup_db)
        eventid = config.mid
        eventmaster = BackendApi.get_scouteventmaster(model_mgr, eventid, using=backup_db)
        
        # CSV作成.
        filename = u'%s.csv' % eventmaster.codename
        
        special_gachas = self.get_special_gachamaster(model_mgr, [9, 48], config.starttime - datetime.timedelta(days=1), config.endtime)
        ranker_num_getter = lambda : BackendApi.get_scoutevent_rankernum(eventid, self.__is_beginer)
        ranking_getter = lambda offset,limit : BackendApi.fetch_uid_by_scouteventrank(eventid, limit, offset, True, self.__is_beginer)
        csv_data = self.__get_csv(filename, ranker_num_getter, ranking_getter, special_gachas)
        if csv_data:
            self.osa_util.write_csv_data(csv_data, filename)
        else:
            self._proc_scout()
    
    def _proc_battle(self):
        """バトルイベント.
        """
        model_mgr = self.getModelMgr()
        
        # 対象のバトルイベント.
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=backup_db)
        eventid = config.mid
        
        # ランキング情報埋め込み.
        special_gachas = self.get_special_gachamaster(model_mgr, [48,20], config.starttime - datetime.timedelta(days=1), config.endtime)
        ranker_num_getter = lambda : BackendApi.get_battleevent_rankernum(eventid, self.__is_beginer)
        ranking_getter = lambda offset,limit : BackendApi.fetch_uid_by_battleeventrank(eventid, limit, offset, True, self.__is_beginer)
        self.__put_ranking(ranker_num_getter, ranking_getter, special_gachas)
        
        eventmaster = BackendApi.get_battleevent_master(model_mgr, eventid, using=backup_db)
        self.__put_csvurl('makebattlecsv', eventmaster)
    
    def _proc_makebattlecsv(self):
        model_mgr = self.getModelMgr()
        
        # 対象のバトルイベント.
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=backup_db)
        eventid = config.mid
        eventmaster = BackendApi.get_battleevent_master(model_mgr, eventid, using=backup_db)
        
        # CSV作成.
        filename = u'%s.csv' % eventmaster.codename
        
        special_gachas = self.get_special_gachamaster(model_mgr, [48,20], config.starttime - datetime.timedelta(days=1), config.endtime)
        ranker_num_getter = lambda : BackendApi.get_battleevent_rankernum(eventid, self.__is_beginer)
        ranking_getter = lambda offset,limit : BackendApi.fetch_uid_by_battleeventrank(eventid, limit, offset, True, self.__is_beginer)
        csv_data = self.__get_csv(filename, ranker_num_getter, ranking_getter, special_gachas)
        if csv_data:
            self.osa_util.write_csv_data(csv_data, filename)
        else:
            self._proc_battle()

    def _proc_produce(self):
        """ プロデュースイベント.
        """
        model_mgr = self.getModelMgr()

        # 対象のプロデュースイベント.
        config = BackendApi.get_current_produce_event_config(model_mgr, using=backup_db)
        eventid = config.mid

        # ランキング情報埋め込み.
        special_gacha_consumetypes = [Defines.GachaConsumeType.STEPUP, Defines.GachaConsumeType.LIMITED_RESET_BOX]
        special_gachas = self.get_special_gachamaster(model_mgr, special_gacha_consumetypes, config.starttime-datetime.timedelta(days=1), config.endtime)
        ranker_num_getter = lambda : BackendApi.get_produceevent_rankernum(eventid)
        ranking_getter = lambda offset, limit: BackendApi.fetch_uid_by_produceeventrank(eventid, limit, offset, withrank=True)
        self.__put_ranking(ranker_num_getter, ranking_getter, special_gachas)

        eventmaster = BackendApi.get_produce_event_master(model_mgr, eventid, using=backup_db)
        self.__put_csvurl('makeproducecsv', eventmaster)

    def _proc_makeproducecsv(self):
        """
        """
        model_mgr = self.getModelMgr()

        # 対象のプロデュースイベント.
        config = BackendApi.get_current_produce_event_config(model_mgr, using=backup_db)
        eventid = config.mid
        eventmaster = BackendApi.get_produce_event_master(model_mgr, eventid, using=backup_db)

        # CSV作成.
        filename = u'{}.csv'.format(eventmaster.codename)

        special_gacha_consumetypes = [Defines.GachaConsumeType.STEPUP, Defines.GachaConsumeType.LIMITED_RESET_BOX]
        special_gachas = self.get_special_gachamaster(model_mgr, special_gacha_consumetypes, config.starttime-datetime.timedelta(days=1), config.endtime)
        ranker_num_getter = lambda : BackendApi.get_produceevent_rankernum(eventid)
        ranking_getter = lambda offset, limit: BackendApi.fetch_uid_by_produceeventrank(eventid, limit, offset, withrank=True)
        csv_data = self.__get_csv(filename, ranker_num_getter, ranking_getter, special_gachas)
        if csv_data:
            self.osa_util.write_csv_data(csv_data, filename=filename)
        else:
            self._proc_produce()

def main(request):
    return Handler.run(request)
