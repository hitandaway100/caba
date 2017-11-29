# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Card import Deck
from platinumegg.app.cabaret.models.Player import PlayerLogin
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.gacha import GachaBoxCardData,\
    GachaBoxGroupData
from defines import Defines
from platinumegg.app.cabaret.models.Gacha import RankingGachaWholePrizeData
from platinumegg.app.cabaret.util.mission import PanelMissionConditionExecuter

class ApiTest(ApiTestBase):
    """マイページ.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__player.lbtime = OSAUtil.get_now()
        self.__player.getModel(PlayerLogin).save()
        
        # デッキ.
        deck = Deck(id=self.__player.id)
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        deck.leader = self.create_dummy(DummyType.CARD, self.__player, cardmaster).id
        
        for i in xrange(9):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            setattr(deck, 'mamber%d' % i, self.create_dummy(DummyType.CARD, self.__player, cardmaster).id)
        
        deck.save()
        
        # お知らせ.
        for _ in range(5):
            self.create_dummy(DummyType.TOP_BANNER_MASTER)
        
        # イベント発生設定.
        config = BackendApi.get_current_scouteventconfig(ModelRequestMgr())
        self.__preconfig_mid = config.mid
        BackendApi.update_scouteventconfig(0, config.starttime, config.endtime)
        
        # カード.
        table = []
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        data = GachaBoxCardData(cardmaster.id, 10000)
        table.append(data.to_data())
        
        # グループ.
        group = self.create_dummy(DummyType.GACHA_GROUP_MASTER, table=table)
        
        # おまけ.
        item = self.create_dummy(DummyType.ITEM_MASTER)
        prize = self.create_dummy(DummyType.PRIZE_MASTER, item=item, itemnum=1)
        bonus = [prize.id]
        
        # ガチャ.
        continuity = 10
        boxdata = GachaBoxGroupData(group.id, 10000, continuity+1)
        box = [boxdata.to_data()]
        self.__gachamaster = self.create_dummy(DummyType.GACHA_MASTER, box=box, bonus=bonus, continuity=continuity, consumetype=Defines.GachaConsumeType.RANKING, consumevalue=10)
        
        # ランキングガチャマスター.
        wholeprizes = {
            'normal' : [(1, bonus),]
        }
        self.__rankingmaster = self.create_dummy(DummyType.RANKING_GACHA_MASTER, self.__gachamaster.boxid, wholeprizes=wholeprizes)
        
        # 達成報酬キュー.
        queue0 = self.create_dummy(DummyType.RANKING_GACHA_WHOLE_PRIZE_QUEUE, self.__rankingmaster.id, point=100, prizes=bonus)
        queue1 = self.create_dummy(DummyType.RANKING_GACHA_WHOLE_PRIZE_QUEUE, self.__rankingmaster.id, point=1000, prizes=bonus)
        self.__queue = queue1
        
        # 初めてプレイした時間.
        self.create_dummy(DummyType.RANKING_GACHA_SCORE, self.__player.id, self.__rankingmaster.id, firstpoint=queue1.point)
        
        # 受け取ったキューのID.
        self.create_dummy(DummyType.RANKING_GACHA_WHOLE_PRIZE_DATA, self.__player.id, queue0.id - 1)
        
        # 全プレ.
        presenteveryone_list = BackendApi.get_presenteveryone_list_formypage(ModelRequestMgr())
        prizeidlist = []
        for presenteveryone in presenteveryone_list:
            prizeidlist.extend(presenteveryone.prizes)
        prizelist = BackendApi.get_prizelist(ModelRequestMgr(), prizeidlist)
        self.__presenteveryone_presentlist = BackendApi.create_present_by_prize(ModelRequestMgr(), 0, prizelist, 0, do_set_save=False)
        
        # ミッション報酬を受け取ってしまう.
        model_mgr = ModelRequestMgr()
        missionplaydata = BackendApi.get_current_panelmission_data(model_mgr, self.__player.id)
        if missionplaydata:
            panel = missionplaydata.mid
            
            # マイページで確認するミッション.
            mission_executer = PanelMissionConditionExecuter()
            
            # 更新確認.
            is_update = BackendApi.check_lead_update_panelmission(model_mgr, self.__player, panel, OSAUtil.get_now(), mission_executer)
            if is_update:
                def write():
                    model_mgr = ModelRequestMgr()
                    if mission_executer.isNeedCheck():
                        BackendApi.tr_complete_panelmission(model_mgr, self.__player.id, mission_executer, OSAUtil.get_now())
                    BackendApi.tr_receive_panelmission(model_mgr, self.__player.id, panel, self.__player.req_confirmkey, OSAUtil.get_now())
                    model_mgr.write_all()
                    model_mgr.write_end()
                write()
        
        self.__present_num = BackendApi.get_present_num(self.__player.id)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def check(self):
        keys = (
            'player',
            'power_total',
            'card',
            'card_num',
            'friend_num',
            'friendrequest_num',
            'free_gacha',
            'present_num',
            'friendlog_list',
            'friendaccept_num',
            'greetlog_list',
            'slidebanners',
            'raidloglist',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        # 受け取ったキューのID.
        wholeprizedata = RankingGachaWholePrizeData.getByKey(self.__player.id)
        if wholeprizedata.queueid != self.__queue.id:
            raise AppTestError(u'ランキングガチャの総計Ptのキューが正しく消化されていない.%d vs %d' % (wholeprizedata.queueid, self.__queue.id))
        
        present_num = BackendApi.get_present_num(self.__player.id)
        ideal_present_num = self.__present_num+1+len(self.__presenteveryone_presentlist)
        if present_num != ideal_present_num:
            raise AppTestError(u'報酬が正しく配布されていない.%d vs %d' % (present_num, ideal_present_num))
    
    def finish(self):
        model_mgr = ModelRequestMgr()
        config = BackendApi.get_current_scouteventconfig(model_mgr)
        config.mid = self.__preconfig_mid
        model_mgr.set_save(config)
        model_mgr.write_all()
        model_mgr.write_end()
