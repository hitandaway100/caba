# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Present import Present

class ApiTest(ApiTestBase):
    """プレゼントボックス.
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        presentidlist = []
        
        # アイテム.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER)
        present = Present.createByItem(0, self.__player0.id, itemmaster)
        present.save()
        presentidlist.append(present.id)
        
        # カード.
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        present = Present.createByCard(0, self.__player0.id, cardmaster)
        present.save()
        presentidlist.append(present.id)
        
        # お金.
        present = Present.createByGold(0, self.__player0.id, 100)
        present.save()
        presentidlist.append(present.id)
        
        # チケット.
        present = Present.createByTicket(0, self.__player0.id, 100)
        present.save()
        presentidlist.append(present.id)
        
        # ガチャポイント.
        present = Present.createByGachaPt(0, self.__player0.id, 100)
        present.save()
        presentidlist.append(present.id)
        
        self.__presentidlist = presentidlist
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/list'
    
    def check(self):
        arr = (
            'presentlist',
            'url_all',
            'url_card',
            'url_item',
            'url_etc',
            'url_receive_all',
            'key_except_card',
            'key_except_gold',
        )
        for k in arr:
            if not self.response.has_key(k):
                raise AppTestError(u'%sが設定されていない' % k)
