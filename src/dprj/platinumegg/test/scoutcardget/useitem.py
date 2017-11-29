# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerGold,\
    PlayerDeck
from defines import Defines
from platinumegg.app.cabaret.util.scout import ScoutDropItemData
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(ApiTestBase):
    """スカウトカード獲得書き込み(アイテムを使用して成功).
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # アイテム.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER, Defines.ItemEffect.SCOUT_CARD_HIGHGRADE, evalue=100)
        item = self.create_dummy(DummyType.ITEM, self.__player0, itemmaster, vnum=1)
        self.__item = item
        
        # ボス.
        boss = self.create_dummy(DummyType.BOSS_MASTER)
        # エリア.
        area = self.create_dummy(DummyType.AREA_MASTER, bossid=boss.id)
        
        # カード.
        cardmaster = self.create_dummy(DummyType.CARD_MASTER, rare=Defines.Rarity.SUPERRARE)
        data = ScoutDropItemData.create(Defines.ItemType.CARD, cardmaster.id, filters={'ptype':Defines.CharacterType.TYPE_001}, rate=10000)
        dropitems = [data.get_dropitem_dict()]
        self.__cardmaster = cardmaster
        
        # スカウト.
        scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area, execution=100, dropitems=dropitems)
        self.__scout = scout
        for _ in xrange(5):
            scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area, opencondition=scout.id)
        
        # 進行情報.
        playdata = self.create_dummy(DummyType.SCOUT_PLAY_DATA, self.__player0.id, self.__scout.id)
        
        # 経験値情報.
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 1, exp=0)
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 2, exp=999)
        self.__player0.level = 1
        self.__player0.exp = 0
        self.__player0.getModel(PlayerExp).save()
        
        self.__player0.gold = 0
        self.__player0.getModel(PlayerGold).save()
        
        self.__player0.cardlimititem = 100
        self.__player0.getModel(PlayerDeck).save()
        
        model_mgr = ModelRequestMgr()
        BackendApi.tr_do_scout(model_mgr, self.__player0, self.__scout, playdata.confirmkey)
        model_mgr.write_all()
        model_mgr.write_end()
        
        self.__cardnum = BackendApi.get_cardnum(self.__player0.id)
        
        self.__playdata = playdata
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%d' % self.__scout.id
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
            Defines.URLQUERY_ID : self.__item.mid,
        }
    
    def check(self):
        model_mgr = ModelRequestMgr()
        uid = self.__player0.id
        
        playdata = BackendApi.get_scoutprogress(model_mgr, uid, [self.__scout.id]).get(self.__scout.id)
        if playdata is None:
            raise AppTestError(u'進行情報がなくなっている')
        
        event = BackendApi.find_scout_event(playdata, Defines.ScoutEventType.GET_CARD)
        if event is None:
            raise AppTestError(u'カード獲得のイベントがない')
        elif not event.is_received:
            raise AppTestError(u'判定処理が行われていない')
        elif not event.is_success:
            raise AppTestError(u'成功フラグが立っていない')
        
        cardnum = BackendApi.get_cardnum(self.__player0.id)
        if (self.__cardnum + 1) != cardnum:
            raise AppTestError(u'カード所持数が想定外')
        
        num = BackendApi.get_item_nums(model_mgr, uid, [self.__item.mid]).get(self.__item.mid)
        if num != (self.__item.num - 1):
            raise AppTestError(u'アイテムの所持数が想定外')
