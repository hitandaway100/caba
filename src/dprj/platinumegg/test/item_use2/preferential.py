# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Item import Item
from defines import Defines
import urllib
from platinumegg.app.cabaret.models.CabaretClub import CabaClubItemPlayerData
import datetime

class ApiTest(ApiTestBase):
    """アイテム使用(優待券配布アイテム).
    """
    def setUp(self):
        self.__now = OSAUtil.get_now()
        # DMMID.
        self.__usenum = 1
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__itemmaster = self.create_dummy(DummyType.ITEM_MASTER, mid=Defines.ItemEffect.CABACLUB_PREFERENTIAL, evalue=30)
        self.__item = self.create_dummy(DummyType.ITEM, self.__player, self.__itemmaster, vnum=self.__usenum, rnum=1)
        # キャバクラのアイテム使用状況.
        self.__itemdata = self.create_dummy(DummyType.CABA_CLUB_ITEM_PLAYER_DATA, self.__player.id, preferential_time=self.__now)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_NUMBER : self.__usenum,
        }
    
    def get_urlargs(self):
        return '/%s/%s' % (self.__itemmaster.id, urllib.quote(self.__player.req_confirmkey, ''))
    
    def check(self):
        item = Item.getByKey(Item.makeID(self.__player.id, self.__itemmaster.id))
        if item is None:
            raise AppTestError(u'アイテムデータがない')
        elif item.vnum != 0:
            raise AppTestError(u'無料分の所持数がおかしい')
        elif item.rnum != self.__item.rnum:
            raise AppTestError(u'課金分の所持数がおかしい')
        itemdata = CabaClubItemPlayerData.getByKey(self.__player.id)
        if itemdata.preferential_id != self.__itemmaster.id:
            raise AppTestError(u'CabaClubItemPlayerDataにアイテムIDが正しく設定されていない')
        elif itemdata.preferential_time < (self.__itemdata.preferential_time + datetime.timedelta(seconds=3600*6)):
            raise AppTestError(u'CabaClubItemPlayerDataの有効期限が正しく設定されていない')
