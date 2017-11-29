# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.card.boxbase import BoxHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines

class Handler(BoxHandler):
    """キャバクラ経営キャスト変更の選択.
    """
    @classmethod
    def getCacheNameSpaceBase(self):
        return 'cabaclubcastselect:%s'
    
    def makeUrlSelf(self):
        return UrlMaker.cabaclubcastselect(self.__mid, self.__cardid)
    
    def __getCardList(self, model_mgr, uid, offset=0, limit=-1):
        cardlist = getattr(self, '_setable_cardlist', None)
        if cardlist is None:
            ctype = self.getCtype()
            sortby = self.getSortby()
            cardlist = self._setable_cardlist = BackendApi.get_cabaclub_setable_cardlist(model_mgr, uid, self.__now, ctype, sortby, using=settings.DB_READONLY)
        if limit == -1:
            return cardlist[offset:]
        else:
            return cardlist[offset:(offset + limit)]
    
    def getCardlist(self, model_mgr, uid, offset, limit):
        cardlist = self.__getCardList(model_mgr, uid, offset, limit)
        return cardlist
    
    def getCardPageNumMax(self, model_mgr, uid):
        cardlist = self.__getCardList(model_mgr, uid)
        num = len(cardlist)
        page = max(1, int((num + self.PAGE_CONTENT_NUM - 1) / self.PAGE_CONTENT_NUM))
        return page
    
    def makeCardObject(self, cardset, deck):
        data = Objects.card(self, cardset, deck=deck)
        url = UrlMaker.cabaclubcastselectdo(self.__mid, self.__cardid, cardset.id)
        data['url_selectdo'] = self.makeAppLinkUrl(url)
        return data
    
    def process(self):
        # 現在時刻.
        self.__now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # ユーザ情報.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        # 店舗のマスターデータ.
        args = self.getUrlArgs('/cabaclubcastselect/')
        mid = args.getInt(0)
        master = None
        if mid:
            master = BackendApi.get_cabaretclub_store_master(model_mgr, mid, using=settings.DB_READONLY)
        if master is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubtop()))
            return
        self.__mid = master.id
        # 削除するID.
        cardid = args.getInt(1)
        card = None
        obj_card = None
        if cardid:
            cardlist = BackendApi.get_cards([cardid], model_mgr, using=settings.DB_READONLY)
            if not cardlist or cardlist[0].card.uid != uid:
                # カードの指定おかしい.
                self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubstore(mid)))
                return
            card = cardlist[0]
            obj_card = Objects.card(self, card)
            obj_card['url_remove'] = self.makeAppLinkUrl(UrlMaker.cabaclubcastremove(mid, cardid))
        self.__cardid = cardid or 0
        # 絞り込みのパラメータ.
        self.loadSortParams(default_sortby=Defines.CardSortType.COST_REV, default_ckind_type=Defines.CardKind.NORMAL, default_maxrare=Defines.Rarity.LIST[-1])
        # カード情報埋め込み.
        self.putCardList()
        # HTML書き出し.
        self.html_param.update(
            current_card = obj_card,
            url_store = self.makeAppLinkUrl(UrlMaker.cabaclubstore(mid)),
        )
        self.writeBoxHtml('cabaclub/castselect')

def main(request):
    return Handler.run(request)
