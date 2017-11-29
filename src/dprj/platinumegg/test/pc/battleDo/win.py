# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Card import Deck
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerDeck, PlayerGold,\
    PlayerKey
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.pc.base import PcTestBase

class ApiTest(PcTestBase):
    """バトル実行(勝利).
    """
    
    def setUp(self):
        # DMMID.
        self.__player = self.makePlayer(1000)
        self.__o_player = self.makePlayer(10)
        self.__o_player.getModel(PlayerGold).save()
        
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100)
        
        # ランク.
        prizes = [{'prizes':[prize.id], 'rate':10}]
        self.__rankmaster = self.create_dummy(DummyType.BATTLE_RANK_MASTER, win=10, times=10, winprizes=prizes, goldkeyrate_base=100)
        # 最大ランクを作っておく.
        self.create_dummy(DummyType.BATTLE_RANK_MASTER, win=10, times=10, winprizes=prizes)
        
        # 対戦相手設定.
        self.__battleplayer = self.create_dummy(DummyType.BATTLE_PLAYER, self.__player.id, self.__rankmaster.id, oid=self.__o_player.id, win=0, times=self.__rankmaster.times - 1)
        
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
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_BATTLE:self.__battleplayer.result,
        }
        return params
    
    def check(self):
        self.checkResponseStatus()
        
        keys = (
            'resultkey',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        model_mgr = ModelRequestMgr()
        # 結果が保存されているか.
        battleresult = BackendApi.get_battleresult(model_mgr, self.__player.id)
        if battleresult is None:
            raise AppTestError(u'結果が保存されていない')
        elif battleresult.result != Defines.BattleResultCode.WIN:
            raise AppTestError(u'結果が想定と違う.%d' % battleresult.result)
        
        # 連勝数が増えているか.
        battleplayer = BackendApi.get_battleplayer(model_mgr, self.__player.id)
        if battleplayer.win_continuity != (self.__battleplayer.win_continuity + 1):
            raise AppTestError(u'連勝数が正しくない.%d vs %d' % (battleplayer.win_continuity, (self.__battleplayer.win_continuity + 1)))
        elif battleplayer.opponent != 0:
            raise AppTestError(u'対戦相手が残っている.')
        
        # 金の鍵を獲得したか.
        playerkey = PlayerKey.getByKey(self.__player.id)
        if playerkey.goldkey != 1:
            raise AppTestError(u'金の鍵が増えていない.')
        
        # プレゼントが増えているか.
        if (self.__present_num + 1) != BackendApi.get_present_num(self.__player.id):
            raise AppTestError(u'プレゼントが届いていない')
