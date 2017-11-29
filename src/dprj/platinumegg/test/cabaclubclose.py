# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.test.cabaclubtestpage import CabaclubTest
from platinumegg.app.cabaret.models.CabaretClub import CabaClubStorePlayerData,\
    CabaClubScorePlayerDataWeekly
from platinumegg.app.cabaret.util.cabaclub_store import CabaclubStoreSet
import datetime

class ApiTest(CabaclubTest):
    """キャバクラ経営店舗閉店.
    """
    
    def setUp(self):
        ua_type = Defines.CabaClubEventUAType.LIVEN_UP
        # ユーザーを用意.
        self.__player = self.create_dummy(DummyType.PLAYER)
        # 店舗を用意.
        cabaclub_dummy = self.setUpCabaclub(self.__player)
        self.__cabaclub_dummy = cabaclub_dummy
        self.__storemaster = cabaclub_dummy.stores[ua_type]
        self.__eventmaster = cabaclub_dummy.events[ua_type]
        self.__exec_cnt = 2
        # キャストを配置しておく.
        self.create_dummy(DummyType.CABA_CLUB_CAST_PLAYER_DATA, self.__player.id, self.__storemaster.id, cabaclub_dummy.cardlist)
        # 前回更新時間を戻しておく.
        storeplayerdata = cabaclub_dummy.storeplayerdata[ua_type]
        storeplayerdata.is_open = True
        storeplayerdata.etime = cabaclub_dummy.now - datetime.timedelta(seconds=Defines.CABARETCLUB_STORE_EVENT_INTERVAL)
        storeplayerdata.utime = cabaclub_dummy.now - datetime.timedelta(seconds=self.__storemaster.customer_interval * self.__exec_cnt)
        storeplayerdata.save()
        self.__storeplayerdata = storeplayerdata
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%d' % self.__storemaster.id
    
    def check(self):
        # 店舗情報の確認.
        storeplayerdata = CabaClubStorePlayerData.getByKey(CabaClubStorePlayerData.makeID(self.__player.id, self.__storemaster.id))
        store = CabaclubStoreSet(self.__storemaster, storeplayerdata)
        if not store.is_alive(OSAUtil.get_now()):
            raise AppTestError(u'期限が切れています')
        elif store.playerdata.is_open:
            raise AppTestError(u'閉店していません')
        elif storeplayerdata.utime.strftime("%Y%m%d%H%M%S") != self.__cabaclub_dummy.now.strftime("%Y%m%d%H%M%S"):
            raise AppTestError(u'utimeが正しくありません')
        elif storeplayerdata.etime.strftime("%Y%m%d%H%M%S") != self.__cabaclub_dummy.now.strftime("%Y%m%d%H%M%S"):
            raise AppTestError(u'etimeが正しくありません')
        elif storeplayerdata.event_id != self.__eventmaster.id:
            raise AppTestError(u'イベントが設定されていません')
        # 獲得ポイントの確認.
        scoredata_weekly = CabaClubScorePlayerDataWeekly.getByKey(self.__cabaclub_dummy.score_weekly.id)
        customer, proceeds = self.calcCustomerAndProceeds(self.__cabaclub_dummy.master, self.__storemaster, self.__exec_cnt, self.__storeplayerdata.scoutman_add, self.__cabaclub_dummy.cardlist, 100 * self.__exec_cnt, 100 * self.__exec_cnt)
        if (storeplayerdata.customer - self.__storeplayerdata.customer) != customer:    # 仮.
            raise AppTestError(u'集客数が正しくありません')
        elif (storeplayerdata.proceeds - self.__storeplayerdata.proceeds) != proceeds:    # 仮.
            raise AppTestError(u'売上が正しくありません')
        elif (scoredata_weekly.customer - self.__cabaclub_dummy.score_weekly.customer) != customer:    # 仮.
            raise AppTestError(u'週間集客数が正しくありません')
        elif (scoredata_weekly.proceeds - self.__cabaclub_dummy.score_weekly.proceeds) != proceeds:    # 仮.
            raise AppTestError(u'週間売上が正しくありません')
