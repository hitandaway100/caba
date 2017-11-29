# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.views.apphandler import AppHandler
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class CardlistHandler(AppHandler):
    """カード合成.
    絞り込み.
        すべて.
        小悪魔.
        大和撫子.
        ツンデレ.
    ソート.
        新着順.
        古い順.
        レアリティが高い順.
        レアリティが低い順.
        レベルが高い順.
        レベルが低い順.
        コストが高い順.
        コストが低い順.
        接客力が高い順.
        接客力が低い順.
    ページング.
    """
    
    PAGE_CONTENT_NUM = Defines.BOX_PAGE_CONTENT_NUM
    
    _put_cardlist = None
    
    def makeUrlSelf(self):
        """このページのURL.
        """
        return None
    
    def getCardlist(self, model_mgr, uid, offset, limit):
        ctype = self.getCtype()
        sortby = self.getSortby()
        cardlist = BackendApi.get_card_list(uid, offset, limit, ctype, sortby, model_mgr, using=settings.DB_READONLY)
        return cardlist
    
    def getCardPageNumMax(self, model_mgr, uid):
        ctype = self.getCtype()
        num = BackendApi.get_cardnum_by_ctype(uid, ctype, model_mgr, using=settings.DB_READONLY)
        page = max(1, int((num + self.PAGE_CONTENT_NUM - 1) / self.PAGE_CONTENT_NUM))
        return page
    
    def makeCardObject(self, cardset, deck):
        return Objects.card(self, cardset, deck=deck)
    
    @classmethod
    def getCacheNameSpaceBase(self):
        return 'cardbox:%s'
    
    def getCtypeOri(self):
        return self.__ctype_ori
    def getCtype(self):
        return self.__ctype
    def getSortby(self):
        return self.__sortby
    def getPage(self):
        return self.__page
    def getCKindType(self):
        return self.__ckind_type
    def getCKindList(self):
        return Defines.CardKind.LIST_FILTER_TABLE.get(self.__ckind_type) or []
    def getMaxRare(self):
        return self.__maxrare
    def getSkillId(self):
        return self.__skillid
    
    def loadSortParams(self, default_ctype='all', default_sortby=Defines.CardSortType.CTIME_REV, default_ckind_type=None, default_maxrare=None, default_skillid=None):
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        client = OSAUtil.get_cache_client()
        
        ctype = default_ctype
        sortby = default_sortby
        page = 0
        ckind_type = default_ckind_type or Defines.CardKind.ListFilterType.CAST_ONLY
        maxrare = default_maxrare if default_maxrare is not None else Defines.Rarity.HIGH_NORMAL
        
        if self.request.method == 'GET':
            namespacebase = self.getCacheNameSpaceBase()
            ctype = client.get(uid, namespace=namespacebase % 'ctype') or ctype
            sortby = client.get(uid, namespace=namespacebase % 'sortby') or sortby
            ckind_type = client.get(uid, namespace=namespacebase % 'ckind_type') or ckind_type
            maxrare = client.get(uid, namespace=namespacebase % 'maxrare') or maxrare
        
        _ctype = self.request.get(Defines.URLQUERY_CTYPE, ctype)
        sortby = self.request.get(Defines.URLQUERY_SORTBY, sortby)
        page = self.request.get(Defines.URLQUERY_PAGE, page)
        ckind_type = self.request.get(Defines.URLQUERY_CKIND, ckind_type)
        maxrare = self.request.get(Defines.URLQUERY_RARE, maxrare)
        skillid = self.request.get(Defines.URLQUERY_SKILL, None)
        
        ctype = _ctype
        if _ctype in ('all', str(Defines.CharacterType.ALL)):
            ctype = None
        elif str(_ctype).isdigit():
            _ctype = int(_ctype)
        
        if str(ckind_type).isdigit():
            ckind_type = int(ckind_type)
        else:
            ckind_type = Defines.CardKind.ListFilterType.CAST_ONLY
        
        if str(maxrare).isdigit():
            maxrare = int(maxrare)
        else:
            maxrare = Defines.Rarity.HIGH_NORMAL
        
        if str(skillid).isdigit():
            skillid = int(skillid)
        else:
            skillid = None
        
        if (ctype is not None and not str(ctype).isdigit()) or not str(page).isdigit() or not Defines.CardSortType.NAMES.has_key(sortby):
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        if ctype:
            ctype = int(ctype)
        if page:
            page = int(page)
        
        self.__ctype_ori = _ctype
        self.__ctype = ctype
        self.__sortby = sortby
        self.__page = page
        self.__ckind_type = ckind_type
        self.__maxrare = maxrare
        self.__skillid = skillid
    
    def getDeckCardIdList(self):
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        deck = BackendApi.get_deck(v_player.id, model_mgr, using=settings.DB_READONLY)
        cardidlist = deck.to_array()[:]
        deck = BackendApi.get_raid_deck(v_player.id, model_mgr, using=settings.DB_READONLY)
        cardidlist.extend(deck.to_array())
        return cardidlist
    
    def putCardList(self):
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        cardidlist = self.getDeckCardIdList()
        
        _ctype = self.getCtypeOri()
        sortby = self.getSortby()
        page = self.getPage()
        ckind_type = self.getCKindType()
        maxrare = self.getMaxRare()
        skillid = self.getSkillId()
        
        offset = page * self.PAGE_CONTENT_NUM
        cardlist = self.getCardlist(model_mgr, v_player.id, offset, self.PAGE_CONTENT_NUM+1)
        has_next = self.PAGE_CONTENT_NUM < len(cardlist)
        cardlist = cardlist[:self.PAGE_CONTENT_NUM]
        self._put_cardlist = cardlist
        
        self.html_param['cardlist'] = [self.makeCardObject(cardset, cardidlist) for cardset in cardlist]
        url = self.makeUrlSelf()
        self.html_param['url_self'] = self.makeAppLinkUrl(url)
        
        url = OSAUtil.addQuery(url, Defines.URLQUERY_CTYPE, _ctype)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_SORTBY, sortby)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_RARE, maxrare)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_CKIND, ckind_type)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_SKILL, skillid)
        if 0 < page:
            self.html_param['url_page_prev'] = self.makeAppLinkUrl(OSAUtil.addQuery(url, Defines.URLQUERY_PAGE, page-1))
        if has_next:
            self.html_param['url_page_next'] = self.makeAppLinkUrl(OSAUtil.addQuery(url, Defines.URLQUERY_PAGE, page+1))
        
        self.html_param['ctype'] = self.getCtype()
        self.html_param['sortby'] = sortby
        self.html_param['cur_page'] = page + 1
        self.html_param['page_max'] = self.getCardPageNumMax(model_mgr, v_player.id)
        
        self.html_param['maxrare'] = maxrare
        self.html_param['ckind_type'] = ckind_type
        self.html_param['skillid'] = skillid
    
    def saveSortParams(self):
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        _ctype = self.getCtypeOri()
        sortby = self.getSortby()
        ckind_type = self.getCKindType()
        maxrare = self.getMaxRare()
        
        client = OSAUtil.get_cache_client()
        namespacebase = self.getCacheNameSpaceBase()
        client.set(uid, _ctype, namespace=namespacebase % 'ctype')
        client.set(uid, sortby, namespace=namespacebase % 'sortby')
        client.set(uid, ckind_type, namespace=namespacebase % 'ckind_type')
        client.set(uid, maxrare, namespace=namespacebase % 'maxrare')
    
