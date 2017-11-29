from platinumegg.app.cabaret.models.TradeShop import TradeShopPlayerData
from django.test import TestCase
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID


class TestTradeShopPlayerData(TestCase):
    fixtures = ['player.json']
    def setUp(self):
        self.uid = 10
        self.tradeshopitemid = 150

    def test_makeID(self):
        makeid = TradeShopPlayerData.makeID(self.uid, self.tradeshopitemid)
        self.assertEqual(makeid, self.uid * (2 ** 32) + self.tradeshopitemid)

    def test_createInstance(self):
        trade_shop_player_data = TradeShopPlayerData.createInstance(TradeShopPlayerData.makeID(self.uid, self.tradeshopitemid))

        self.assertTrue(isinstance(trade_shop_player_data, TradeShopPlayerData))
        self.assertEqual(trade_shop_player_data.id, TradeShopPlayerData.makeID(self.uid, self.tradeshopitemid))
        self.assertEqual(trade_shop_player_data.uid, self.uid)
        self.assertEqual(trade_shop_player_data.mid, self.tradeshopitemid)
        self.assertEqual(trade_shop_player_data.cnt, 0)

    def test_subclass(self):
        self.assertTrue(issubclass(TradeShopPlayerData,BasePerPlayerBaseWithMasterID))
