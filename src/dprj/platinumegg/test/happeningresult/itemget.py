# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerGold
from defines import Defines
from platinumegg.app.cabaret.util.scout import ScoutDropItemData
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import urllib

class ApiTest(ApiTestBase):
    """ハプニング実行アニメ(アイテム獲得).
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        items = []
        
        # アイテム.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER)
        data = ScoutDropItemData.create(Defines.ItemType.ITEM, itemmaster.id, filters={'ptype':Defines.CharacterType.TYPE_001}, rate=10000)
        items.append(data.get_dropitem_dict())
        self.__itemmaster = itemmaster
        
        # レイド.
        raidmaster = self.create_dummy(DummyType.RAID_MASTER)
        
        # ハプニング.
        happeningmaster = self.create_dummy(DummyType.HAPPENING_MASTER, raidmaster.id, items=items)
        self.__happeningmaster = happeningmaster
        
        # ハプニング情報.
        happening = self.create_dummy(DummyType.HAPPENING, self.__player0.id, self.__happeningmaster.id)
        self.__happening = happening
        
        # 経験値情報.
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 1, exp=0)
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 2, exp=999)
        self.__player0.level = 1
        self.__player0.exp = 0
        self.__player0.getModel(PlayerExp).save()
        
        self.__player0.gold = 0
        self.__player0.getModel(PlayerGold).save()
        
        model_mgr = ModelRequestMgr()
        BackendApi.tr_do_happening(model_mgr, self.__player0, self.__happeningmaster, self.__player0.req_confirmkey)
        model_mgr.write_all()
        model_mgr.write_end()
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%s' % urllib.quote(self.__player0.req_confirmkey, safe='')
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        keys = (
            'player',
            'happening',
            'url_exec',
            'url_happeningcancel_yesno',
            'item',
            'raidhelplist',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
