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
import urllib

class ApiTest(ApiTestBase):
    """スカウト実行演出(カード発見).
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # ボス.
        boss = self.create_dummy(DummyType.BOSS_MASTER)
        # エリア.
        area = self.create_dummy(DummyType.AREA_MASTER, bossid=boss.id)
        
        # カード.
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
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
        
        self.__playdata = playdata
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%d/%s' % (self.__scout.id, urllib.quote(self.__playdata.confirmkey, safe=''))
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        keys = (
            'dataBody',
            'dataUrl',
            'topUrl',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
