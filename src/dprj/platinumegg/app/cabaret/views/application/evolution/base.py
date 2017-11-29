# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.views.application.cardlisthandler import CardlistHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker


class EvolutionHandler(CardlistHandler):
    """進化合成.
    """
    
    def makeUrlSelf(self):
        return None
    
    def writeEvolutionHtml(self, name):
        """HTML書き出し.
        """
        v_player = self.getViewerPlayer()
        
        _ctype = self.getCtypeOri()
        sortby = self.getSortby()
        page = self.getPage()
        
        self.html_param[Defines.URLQUERY_CTYPE] = _ctype
        self.html_param[Defines.URLQUERY_SORTBY] = sortby
        self.html_param[Defines.URLQUERY_PAGE] = page
        
        ctype_items = {
            'all' : u'全て'
        }
        ctype_items.update(Defines.CharacterType.NAMES)
        self.html_param['ctype_items'] = ctype_items.items()
        self.html_param['sort_items'] = Defines.CardSortType.NAMES.items()
        
        client = OSAUtil.get_cache_client()
        namespacebase = self.getCacheNameSpaceBase()
        client.set(v_player.id, _ctype, namespace=namespacebase % 'ctype')
        client.set(v_player.id, sortby, namespace=namespacebase % 'sortby')
        client.set(v_player.id, page, namespace=namespacebase % 'page')
        
        self.writeAppHtml(name)
    
    def getMaterialId(self):
        str_cardid = self.request.get(Defines.URLQUERY_CARD, None)
        return int(str_cardid)
    
    def checkBaseCard(self, basecard):
        v_player = self.getViewerPlayer()
        if basecard is None or basecard.card.uid != v_player.id or not basecard.is_can_evolution:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'不正なキャストです.%d' % basecard.id)
            url = UrlMaker.evolution()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return False
        return True
    
    def checkMaterialCard(self, basecard, materialcard, deck):
        v_player = self.getViewerPlayer()
        if materialcard is None or materialcard.id == basecard.id or materialcard.card.protection or deck.is_member(materialcard.id) or basecard.card.uid != v_player.id:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'ハメ管理に選択できないキャストです.', CabaretError.Code.ILLEGAL_ARGS)
            url = UrlMaker.evolution()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return False
        return True
