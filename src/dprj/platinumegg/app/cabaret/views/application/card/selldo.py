# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerGold, PlayerTreasure
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.Card import Card


class Handler(AppHandler):
    """カード売却.
    完了に渡すパラメータ:
        売却した枚数.
        売却金額の合計.
        所持金.
        売却後の所持金.
    エラー:
        存在しないカードを選んだ.
        他プレイヤーのカードを選んだ.
        デッキのカードを選んだ.
        保護中のカードを選んだ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold, PlayerTreasure]
    
    def process(self):
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        try:
            str_cardidlist = self.request.get(Defines.URLQUERY_CARD, None)
            cardidlist = [int(str_cardid) for str_cardid in str_cardidlist.split(',')]
            if len(cardidlist) == 0:
                raise
        except:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        cardidlist = list(set(cardidlist))
        cardlist = model_mgr.get_models(Card, cardidlist, False, using=settings.DB_DEFAULT)
        if len(cardlist) != len(cardidlist):
            raise CabaretError(u'キャストが見つかりませんでした', CabaretError.Code.NOT_DATA)
        
        wrote_model_mgr, sellprice, sellprice_treasure = db_util.run_in_transaction(Handler.tr_write, v_player.id, cardidlist)
        wrote_model_mgr.write_end()
        
        playergold = wrote_model_mgr.get_wrote_model(PlayerGold, v_player.id, PlayerGold.getByKey, v_player.id)
        
        url = UrlMaker.sellcomplete()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_CARD_NUM, len(cardidlist))
        url = OSAUtil.addQuery(url, Defines.URLQUERY_GOLD, playergold.gold)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_GOLDADD, sellprice)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_GOLDPRE, v_player.gold)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_CABAKING, sellprice_treasure)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_CABAKINGPRE, v_player.cabaretking)
        
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    @staticmethod
    def tr_write(uid, cardidlist):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        sellprice, sellprice_treasure = BackendApi.tr_sell_card(model_mgr, uid, cardidlist)
        model_mgr.write_all()
        return model_mgr, sellprice, sellprice_treasure

def main(request):
    return Handler.run(request)
