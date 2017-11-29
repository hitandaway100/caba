# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Card import Deck
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerDeck, PlayerGold,\
    PlayerKey
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(ApiTestBase):
    """バトル実行(ランクアップ).
    """
    
    def setUp(self):
        # DMMID.
        self.__player = self.makePlayer(1000)
        self.__o_player = self.makePlayer(10)
        self.__o_player.getModel(PlayerGold).save()
        
        # 報酬.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER, mid=Defines.ItemEffect.ACTION_SMALL_RECOVERY, evalue=2)
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100, item=itemmaster)
        
        # ランク.
        prizes = [{'prizes':[prize.id], 'rate':10}]
        self.__rankmaster = self.create_dummy(DummyType.BATTLE_RANK_MASTER, win=10, times=10, rankupprizes=prizes, goldkeyrate_base=0)
        # 最大ランクを作っておく.
        self.create_dummy(DummyType.BATTLE_RANK_MASTER, win=10, times=10, rankupprizes=prizes)
        
        # 対戦相手設定.
        self.__battleplayer = self.create_dummy(DummyType.BATTLE_PLAYER, self.__player.id, self.__rankmaster.id, oid=self.__o_player.id, win=self.__rankmaster.win, times=self.__rankmaster.times)
        
        # 書き込み前のプレゼント数.
        self.__present_num = BackendApi.get_present_num(self.__player.id)
    
    def makePlayer(self, power):
        player = self.create_dummy(DummyType.PLAYER)
        player.deckcapacitylv = 999
        player.getModel(PlayerDeck).save()
        
        # デッキ.
        deck = Deck(id=player.id)
        
        arr = []
        for _ in xrange(Defines.DECK_CARD_NUM_MAX - 3):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER, basepower=power, maxpower=power)
            card = self.create_dummy(DummyType.CARD, player, cardmaster)
            arr.append(card.id)
        deck.set_from_array(arr)
        deck.save()
        
        return player
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return '/%d' % (self.__battleplayer.result)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        model_mgr = ModelRequestMgr()
        # 結果が保存されているか.
        battleresult = BackendApi.get_battleresult(model_mgr, self.__player.id)
        if battleresult is None:
            raise AppTestError(u'結果が保存されていない')
        elif battleresult.result != Defines.BattleResultCode.WIN:
            raise AppTestError(u'結果が想定と違う.%d' % battleresult.result)
        
        # 連勝数が増えているか.
        battleplayer = BackendApi.get_battleplayer(model_mgr, self.__player.id)
        if battleplayer.win_continuity != 0:
            raise AppTestError(u'連勝数が正しくない.')
        elif battleplayer.times != 0:
            raise AppTestError(u'ノルマ数が正しくない.')
        elif battleplayer.opponent != 0:
            raise AppTestError(u'対戦相手が残っている.')
        
        # 銀の鍵を獲得したか.
        playerkey = PlayerKey.getByKey(self.__player.id)
        if playerkey.silverkey != 1:
            raise AppTestError(u'銀の鍵が増えていない.')
        
        # プレゼントが増えているか.
        if (self.__present_num + 1) != BackendApi.get_present_num(self.__player.id):
            raise AppTestError(u'プレゼントが届いていない')
        
        # お金が増えているか.
        playergold = model_mgr.get_model(PlayerGold, self.__player.id)
        if playergold.gold != (self.__player.gold+100):
            raise AppTestError(u'報酬のお金が付与されていない')
