# -*- coding: utf-8 -*-

from django.test import TestCase
from unittest import TestCase as stdTestCase
from django.utils.unittest import TestSuite, TestLoader, TextTestRunner
from platinumegg.app.cabaret.models.Player import BasePerPlayerBase,\
    Player, PlayerTutorial, PlayerDeck, PlayerTreasure, PlayerTradeShop, PlayerLogin, PlayerLoginTimeLimited,\
    RareCardLog
from platinumegg.app.cabaret.models.Card import Card
from platinumegg.app.cabaret.models.base.models import BaseModel
from platinumegg.lib.opensocial.util import OSAUtil

class TestBasePerPlayerBase(TestCase):
    def setUp(self):
        self.uid = 11
        self.mid = 321

    def test_makeID(self):
        maked_id = BasePerPlayerBase.makeID(self.uid, self.mid)
        self.assertEqual(maked_id, self.uid * (2 ** 32) + self.mid)

    def test_makeInstance(self):
        maked_id = BasePerPlayerBase.makeID(self.uid, self.mid)
        base_per_player_base = BasePerPlayerBase.makeInstance(maked_id)

        self.assertTrue(isinstance(base_per_player_base, BasePerPlayerBase))
        self.assertEqual(base_per_player_base.uid, self.uid)
        self.assertEqual(base_per_player_base.mid, self.mid)

    def test_subclass(self):
        issubclass(BasePerPlayerBase, BaseModel)


class TestPlayerTutorial(TestCase):
    fixtures = ["playertutorial.json", "player.json"]

    def setUp(self):
        self.models = PlayerTutorial.objects.all()

    def test_returns_tutorialstate(self):
        # 0xff(16) -> 0b1111111100000000(2) -> 65280(10)
        # 255(10)以下だと0

        for model in self.models:
            state = model.returns_tutorialstate
            self.assertEqual(state, model.tutorialstate & 0xff00)

    def test_subclass(self):
        self.assertTrue(issubclass(PlayerTutorial, BaseModel))


class TestPlayerDeck(TestCase):
    fixtures = ["playerdeck.json", "player.json"]

    def setUp(self):
        self.models = PlayerDeck.objects.all()

    def test_cardlimit(self):
        for model in self.models:
            cardlimit = model.cardlimit
            self.assertEqual(cardlimit, model.cardlimitlv + model.cardlimititem)

    def test_deckcapacity(self):
        for model in self.models:
            deckcapacity = model.deckcapacity
            self.assertEqual(deckcapacity, model.deckcapacitylv + model.deckcapacityscout)

    def test_subclass(self):
        self.assertTrue(issubclass(PlayerDeck, BaseModel))


class TestPlayerTreasure(TestCase):
    fixtures = ["playertreasure.json", "player.json"]

    def setUp(self):
        self.model = PlayerTreasure.objects.get(pk=1)
        self.models = PlayerTreasure.objects.all()

    def test_get_cabaretking_num(self):
        for model in self.models:
            get_cabaretking_num = model.get_cabaretking_num()
            self.assertEqual(get_cabaretking_num, model.cabaretking + model.demiworld)

    def test_subclass(self):
        issubclass(PlayerTreasure, BaseModel)


class TestPlayerTradeShop(TestCase):
    fixtures = ["player.json"]

    def setUp(self):
        pass

    def test_get(self):
        pass

    def test_createInstance(self):
        player = Player.objects.get(pk=1)
        player_trade_shop = PlayerTradeShop.createInstance(player.id)

        self.assertTrue(isinstance(player_trade_shop, PlayerTradeShop))
        self.assertEqual(player_trade_shop.point, 0)
        self.assertEqual(player_trade_shop.id, player.id)

    def test_subclass(self):
        issubclass(PlayerTradeShop, BaseModel)


class TestPlayerLogin(TestCase):
    fixtures = ["playerlogin.json", "player.json"]

    def setUp(self):
        self.playerlogin = PlayerLogin.objects.get(pk=1)
        self.loginbonusmaster_id = 1
        self.loginbonusmaster_id_different = 100
        self.playerlogin.tlmid = self.loginbonusmaster_id

    def test_getDays(self):
        tldays = self.playerlogin.getDays(self.loginbonusmaster_id)
        self.assertEqual(tldays, self.playerlogin.tldays)

        tldays = self.playerlogin.getDays(0)
        self.assertEqual(tldays, 0)

        tldays = self.playerlogin.getDays(self.loginbonusmaster_id_different)
        self.assertEqual(tldays, 0)

    def test_getDaysView(self):
        tldays = self.playerlogin.getDaysView(self.loginbonusmaster_id)
        self.assertEqual(tldays, self.playerlogin.tldays_view)

        tldays = self.playerlogin.getDaysView(0)
        self.assertEqual(tldays, 0)

        tldays = self.playerlogin.getDaysView(self.loginbonusmaster_id_different)
        self.assertEqual(tldays, 0)

    def test_subclass(self):
        issubclass(PlayerLogin, BaseModel)


class TestPlayerLoginTimeLimited(TestCase):
    fixtures = ["playerlogintimelimited.json", "player.json"]

    def setUp(self):
        self.models = PlayerLoginTimeLimited.objects.all()

    def test_getDays(self):
        for model in self.models:
            days = model.getDays(model.mid)
            self.assertEqual(days, model.days)

        days = PlayerLoginTimeLimited().getDays(0)
        self.assertEqual(days, 0)

    def test_subclass(self):
        issubclass(PlayerLoginTimeLimited, BaseModel)


class TestRareCardLog(TestCase):
    fixtures = ["rarecardlog.json", "player.json", "card.json", "cardmaster.json"]

    def setUp(self):
        self.models = RareCardLog.objects.all()
        self.cardmasterid = Card.objects.all()[0].mid

    def test_add(self):
        for model in self.models:
            card0 = model.card0
            gtime0 = model.gtime0
            model.add(self.cardmasterid)
            self.assertTrue(isinstance(model, RareCardLog))
            self.assertEqual(model.card1, card0)
            self.assertEqual(model.gtime1, gtime0)
            self.assertEqual(model.card0, self.cardmasterid)
            self.assertEqual(model.gtime0.second, OSAUtil.get_now().second)

    def test_to_array(self):
        rarecardlog_card1on = RareCardLog.objects.get(pk=1)
        rarecardlog_card1on.card1 = 11111
        rarecardlog_on_array = rarecardlog_card1on.to_array()
        self.assertEqual(rarecardlog_on_array[0]['card'], rarecardlog_card1on.card0)
        self.assertEqual(rarecardlog_on_array[0]['time'], rarecardlog_card1on.gtime0)
        self.assertEqual(rarecardlog_on_array[1]['card'], rarecardlog_card1on.card1)
        self.assertEqual(rarecardlog_on_array[1]['time'], rarecardlog_card1on.gtime1)

        rarecardlog_card1off = RareCardLog.objects.get(pk=1)
        rarecardlog_card1off.card1 = 0
        rarecardlog_off_array = rarecardlog_card1off.to_array()
        self.assertEqual(len(rarecardlog_off_array), 1)
        self.assertEqual(rarecardlog_off_array[0]['card'], rarecardlog_card1off.card0)
        self.assertEqual(rarecardlog_off_array[0]['time'], rarecardlog_card1off.gtime0)

    def test_subclass(self):
        issubclass(RareCardLog, BaseModel)


class PlayerAllRun(stdTestCase):
    def test_allrun(self):
        loader = TestLoader()
        base_per_player_base = loader.loadTestsFromTestCase(TestBasePerPlayerBase)
        player_tutorial = loader.loadTestsFromTestCase(TestPlayerTutorial)
        player_deck = loader.loadTestsFromTestCase(TestPlayerDeck)
        player_treasure = loader.loadTestsFromTestCase(TestPlayerTreasure)
        player_trade_shop = loader.loadTestsFromTestCase(TestPlayerTradeShop)
        player_login = loader.loadTestsFromTestCase(TestPlayerLogin)
        player_login_time_limited = loader.loadTestsFromTestCase(TestPlayerLoginTimeLimited)
        rare_card_log = loader.loadTestsFromTestCase(TestRareCardLog)
        tests = TestSuite([base_per_player_base, player_tutorial, player_deck,
                           player_treasure, player_trade_shop, player_login,
                           player_login_time_limited, rare_card_log])
        TextTestRunner().run(tests)
