# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.composition.base import CompositionHandler
from platinumegg.app.cabaret.models.Player import PlayerGold, PlayerRequest
from platinumegg.app.cabaret.util.api import Objects, BackendApi
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines


class Handler(CompositionHandler):
    """合成確認.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold, PlayerRequest]
    
    def getCardlist(self, model_mgr, uid, offset, limit):
        cardlist = BackendApi.get_cards(self.__materialidlist, model_mgr, using=settings.DB_READONLY)
        self.__include_rare = False
        for card in cardlist:
            if Defines.Rarity.RARE <= card.master.rare:
                self.__include_rare = True
                break
        return cardlist
    
    def getCardPageNumMax(self, model_mgr, uid):
        return 1
    
    def makeUrlSelf(self):
        return ''
    
    def makeCardObject(self, cardset, deck):
        obj_card = Objects.card(self, cardset, deck=deck)
        if cardset.card.id == self.__baseid or cardset.card.protection or obj_card['deckmember']:
            raise CabaretError(u'パートナーに選択できないキャストです.', CabaretError.Code.ILLEGAL_ARGS)
        url = UrlMaker.compositionmaterial(self.__baseid)
        obj_card['url_composition'] = self.makeAppLinkUrl(url)
        return obj_card
    
    def process(self):
        self.__include_rare = False
        
        args = self.getUrlArgs('/compositionyesno/')
        try:
            self.__baseid = int(args.get(0))
            self.__materialidlist = self.getMaterialIdList()
        except:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
            url = UrlMaker.composition()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        # ベースカード.
        basecard = BackendApi.get_cards([self.__baseid], model_mgr, using=settings.DB_READONLY)
        if not basecard or basecard[0].card.uid != v_player.id:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'不正なキャストです.%d' % self.__baseid)
            url = UrlMaker.composition()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        basecard = basecard[0]
        self.html_param['basecard'] = Objects.card(self, basecard)
        
        self.loadSortParams()
        
        # プレイヤー情報.
        self.html_param['player'] = Objects.player(self, v_player)
        
        # カード.
        self.putCardList()
        if not self._put_cardlist:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'素材が選ばれていません')
            url = UrlMaker.composition()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        card_masters = {m.master for m in self._put_cardlist if m.master.ckind == Defines.CardKind.SKILL}
        
        is_not_skillup = False
        for card_master in card_masters:
            if card_master.id != Defines.MasterData.TIARA_ID and card_master.rare < basecard.master.rare:
                is_not_skillup = True
                break
        self.html_param['not_skillup'] = is_not_skillup

        # 消費ゴールド.
        cost = BackendApi.calc_composition_cost(basecard, self._put_cardlist)
        self.html_param['cost'] = cost
        self.html_param['cost_over'] = v_player.gold < cost
        self.html_param['gold_post'] = v_player.gold - cost
        
        self.html_param['cardnum'] = BackendApi.get_cardnum(v_player.id, model_mgr, using=settings.DB_READONLY)
        
        # 書き込みへのURL.
        str_cardidlist = ','.join([str(cardset.card.id) for cardset in self._put_cardlist])
        url = UrlMaker.compositiondo(self.__baseid, v_player.req_confirmkey)
        self.html_param['url_do'] = self.makeAppLinkUrl(OSAUtil.addQuery(url, Defines.URLQUERY_CARD, str_cardidlist))
        
        self.html_param['flag_include_rare'] = self.__include_rare
        
        self.writeAppHtml('composition/yesno')

def main(request):
    return Handler.run(request)
