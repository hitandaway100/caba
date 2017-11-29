# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Item import Item
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerAp
from platinumegg.test.pc.base import PcTestBase

class ApiTest(PcTestBase):
    """アイテム使用(体力回復).
    """
    def setUp(self):
        # DMMID.
        self.__usenum = 1
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__itemmaster = self.create_dummy(DummyType.ITEM_MASTER, mid=Defines.ItemEffect.ACTION_SMALL_RECOVERY, evalue=2)
        self.__item = self.create_dummy(DummyType.ITEM, self.__player, self.__itemmaster, vnum=self.__usenum, rnum=1)
        
        self.__player.apmax = 999
        self.__player.set_ap(0)
        self.__player.getModel(PlayerAp).save()
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_NUMBER : self.__usenum,
            Defines.URLQUERY_ITEM : self.__itemmaster.id,
            Defines.URLQUERY_CURRENT : self.__item.num,
        }
    
    def check(self):
        self.checkResponseStatus()
        
        keys = (
            'item',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        item = Item.getByKey(Item.makeID(self.__player.id, self.__itemmaster.id))
        if item is None:
            raise AppTestError(u'アイテムデータがない')
        elif item.vnum != 0:
            raise AppTestError(u'無料分の所持数がおかしい')
        elif item.rnum != self.__item.rnum:
            raise AppTestError(u'課金分の所持数がおかしい')
        
        playerap = PlayerAp.getByKey(self.__player.id)
        if playerap.ap != (self.__itemmaster.evalue * self.__usenum):
            raise AppTestError(u'体力が回復していない')
        