# -*- coding: utf-8 -*-
import datetime
from platinumegg.app.cabaret.models.CabaretClub import CabaClubStorePlayerData,\
    CabaClubItemPlayerData, CabaClubEventMaster
from platinumegg.lib.opensocial.util import OSAUtil
from collections import namedtuple
from random import randint
from defines import Defines
from platinumegg.app.cabaret.models.Item import ItemMaster
import settings

class CabaclubStoreSet:
    """キャバクラ店舗.
    """
    def __init__(self, master, playerdata, itemdata=None, eventmaster=None):
        self.__master = master
        self.__playerdata = playerdata or CabaClubStorePlayerData.makeInstance(0)
        self.__itemdata = itemdata or CabaClubItemPlayerData.makeInstance(0)
        self.__eventmaster = eventmaster
        self.__loaded_events = None
        self.__rental_cost = None
    
    @property
    def master(self):
        return self.__master
    @property
    def playerdata(self):
        return self.__playerdata
    @property
    def itemdata(self):
        return self.__itemdata
    @property
    def eventmaster(self):
        return self.__eventmaster
    
    def get_limit_time(self):
        """店舗の有効期限.
        """
        return self.playerdata.ltime
    
    def __load_rental_cost(self):
        if self.__rental_cost is None:
            self.__rental_cost = {}
            master = self.master
            idx = 0
            while True:
                days = getattr(master, 'days_{}'.format(idx), None)
                if days is None:
                    break
                elif 0 < days:
                    cost = getattr(master, 'cost_{}'.format(idx))
                    self.__rental_cost[days] = cost
                idx += 1
        return self.__rental_cost
    
    def get_rental_cost_dict(self):
        """店舗の借り入れコストテーブル.
        """
        return self.__load_rental_cost()
    
    def get_rental_cost(self, days):
        """店舗の借り入れコスト.
        存在しない場合はNone.
        """
        return self.__load_rental_cost().get(days, None)
    
    def get_current_preferential_item_id(self, now):
        """現在有効な優待券配布アイテムのID.
        """
        if self.itemdata is not None and now < self.itemdata.preferential_time:
            return self.itemdata.preferential_id
        else:
            return 0
    
    def get_current_barrier_item_id(self, now):
        """現在有効なバリア的なアイテムのID.
        """
        if self.itemdata is not None and now < self.itemdata.barrier_time:
            return self.itemdata.barrier_id
        else:
            return 0
    
    def is_alive(self, now=None):
        """店舗が有効か.
        """
        now = now or OSAUtil.get_now()
        return now < self.get_limit_time()
    
    EventData = namedtuple("EventData", "events,rate_total,rate_total_preferential")
    def __setup_events(self, model_mgr):
        if self.__loaded_events is None:
            rate_total = 0
            rate_total_preferential = 0
            events = []
            eventmaster_dict = dict([(eventmaster.id, eventmaster) for eventmaster in model_mgr.get_mastermodel_all(CabaClubEventMaster, using=settings.DB_READONLY) if eventmaster.ua_type != Defines.CabaClubEventUAType.TAKE_MEASURES])
            for eventid, rate in self.master.events:
                if 0 < rate:
                    preferential = eventmaster_dict.get(eventid, None) is not None
                    events.append((eventid, (rate, preferential)))
                    rate_total += rate
                    if preferential:
                        rate_total_preferential += rate
            self.__loaded_events = CabaclubStoreSet.EventData(events, rate_total,rate_total_preferential)
        return self.__loaded_events
    
    def select_event(self, model_mgr, now):
        """発生するイベント選択.
        """
        # イベント発生テーブルを準備.
        eventdata = self.__setup_events(model_mgr)
        if eventdata.rate_total < 1:
            # 発生するイベントがない.
            return None
        
        # バリアアイテム.
        barrier_item_id = self.get_current_barrier_item_id(now)
        if barrier_item_id:
            # イベントが発生しない.
            return None
        
        # 優待券配布アイテム.
        preferential_item_id = self.get_current_preferential_item_id(now)
        preferential_item = model_mgr.get_model(ItemMaster, preferential_item_id, using=settings.DB_READONLY) if preferential_item_id else None
        event_rate_correction = (preferential_item.evalue if preferential_item else 0)
        
        # ランダム.
        v = randint(1, 10000)
        if (eventdata.rate_total * (event_rate_correction + 100) / 100) < v:
            # イベントが発生しない.
            return None
        # 発生するイベントを選ぶ.
        v = randint(0, eventdata.rate_total + eventdata.rate_total_preferential * event_rate_correction / 100)
        for eventid, data in eventdata.events:
            rate, preferential = data
            if preferential:
                # 補正対象のイベント.
                rate = rate * (event_rate_correction+100) / 100
            v -= rate
            if v < 1:
                return eventid
        return None
    
    def set_event(self, eventmaster, etime, ua_flag=False):
        """イベントの設定.
        """
        self.playerdata.event_id = eventmaster.id if eventmaster else 0
        self.playerdata.etime = etime
        self.playerdata.ua_flag = ua_flag
        self.__eventmaster = eventmaster
    
    def get_customer_up_by_event(self):
        """イベント発生による集客数の補正値.
        """
        if not self.eventmaster:
            return 100
        elif not self.playerdata.ua_flag:
            # ユーザーアクションがまだ実行されていない.
            return self.eventmaster.customer_up
        elif self.eventmaster.ua_type == Defines.CabaClubEventUAType.LIVEN_UP:
            # 盛り上げた.
            return 100 + (self.eventmaster.customer_up - 100) * self.eventmaster.ua_value / 100
        else:
            # その他.
            return self.eventmaster.customer_up
    
    def get_proceeds_up_by_event(self):
        """イベント発生による売上の補正値.
        """
        if not self.eventmaster:
            return 100
        elif not self.playerdata.ua_flag:
            # ユーザーアクションがまだ実行されていない.
            return self.eventmaster.proceeds_up
        elif self.eventmaster.ua_type == Defines.CabaClubEventUAType.LIVEN_UP:
            # 盛り上げた.
            return 100 + (self.eventmaster.proceeds_up - 100) * self.eventmaster.ua_value / 100
        else:
            # その他.
            return self.eventmaster.proceeds_up
    
    def get_event_endtime(self):
        """店舗で発生しているイベントの終了時間.
        """
        if self.eventmaster:
            event_endtime = self.playerdata.etime + datetime.timedelta(seconds=self.eventmaster.seconds)
        else:
            event_endtime = self.playerdata.etime
        return min(event_endtime, self.get_limit_time())
    
    def get_current_eventmaster(self, now):
        """店舗で発生しているイベント.
        """
        if now < self.get_event_endtime():
            return self.eventmaster
        return None
    
    def get_scoutman_addable_num(self):
        """追加可能なスカウトマン数.
        """
        return max(0, self.master.scoutman_add_max - self.playerdata.scoutman_add)
