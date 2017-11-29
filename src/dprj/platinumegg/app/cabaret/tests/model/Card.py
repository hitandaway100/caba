# -*- coding: utf-8 -*-

from django.test import TestCase
from platinumegg.app.cabaret.models.Card import CardMaster, Card, CardDeleted,\
    Deck, CompositionData
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.util.card import CardSet


class TestCardMaster(TestCase):
    fixtures = ["cardmaster.json"]

    def setUp(self):
        self.album = 255
        self.hklevel = 10
        self.albumhklevel = CardMaster.makeAlbumHklevel(self.album, self.hklevel)
        self.models = CardMaster.objects.all()

    def test_makeAlbumHklevel(self):
        for model in self.models:
            albumhklevel = model.makeAlbumHklevel(model.album, model.hklevel)
            self.assertEqual(albumhklevel, model.albumhklevel)

    def test_album(self):
        for model in self.models:
            album = model.album
            self.assertEqual(album, model.album)

    def test_hklevel(self):
        for model in self.models:
            hklevel = model.hklevel
            self.assertEqual(hklevel, model.hklevel)


class TestCardDeleted(TestCase):
    fixtures = ["card.json", "cardmaster.json", "player.json"]

    def setUp(self):
        # 基本情報をまず取得.
        self.player = Player.objects.get(pk=1)
        self.card = Card.objects.filter(uid=self.player.id)[0]

    def test_create(self):
        card_deleted = CardDeleted().create(self.card)
        self.assertTrue(card_deleted, CardDeleted)

        for field in self.card._meta.fields:
            self.assertEqual(getattr(card_deleted, field.name), getattr(self.card, field.name))


class TestDeck(TestCase):
    fixtures = ["deck.json", "player.json"]

    def setUp(self):
        self.deck = Deck.objects.get(pk=1)

    def test_to_array(self):
        self.assertTrue(isinstance(self.deck, Deck))
        target_arr = set(self.deck.to_array())
        origin_arr = set(self._get_member_values(self.deck))

        self.assertEqual(target_arr, origin_arr)

    def test_set_from_array(self):
        instance = Deck()
        self.assertRaises(CabaretError, instance.set_from_array, [])

        instance.set_from_array(self.deck.to_array())
        target_arr = set(instance.to_array())
        origin_arr = set(self.deck.to_array())
        self.assertEqual(target_arr, origin_arr)

    def test_is_member(self):
        for member_value in self.deck.to_array():
            self.assertTrue(self.deck.is_member(member_value))

    def _get_member_values(self, deck):
        return [getattr(deck, "member%d" % x) for x in xrange(1, 10)] + [getattr(deck, "leader")]


class TestCompositionData(TestCase):
    fixtures = ["compositiondata.json", "player.json", "card.json", "cardmaster.json"]

    def setUp(self):
        self.compositions = CompositionData.objects.all()
        self.cards = Card.objects.all()

    def test_set_card(self):
        card = Card.objects.all()[0]
        composition = CompositionData.objects.all()[0]
        composition.set_to_card(card)
        for field in CompositionData._meta.fields:
            if field.name != "id" and field.name != "result":
                self.assertEqual(getattr(card, field.name), getattr(composition, field.name))

    def test_setBasePerParameter(self):
        for card in self.cards:
            base = CompositionData()
            base.setBasePreParameter(card)
            for field in CompositionData._meta.fields:
                if field.name != "id" and field.name != "result":
                    self.assertEqual(getattr(base, field.name), getattr(card, field.name))
