# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.app.cabaret.views.application.cardlisthandler import CardlistHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class CompositionHandler(CardlistHandler):
    """カード合成.
    """
    
    def makeUrlSelf(self):
        return None
    
    def writeCompositionHtml(self, name):
        """HTML書き出し.
        """
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
        
        self.saveSortParams()
        
        self.writeAppHtml(name)
    
    def getMaterialIdList(self):
        cardidlist = []
        for i in xrange(CompositionHandler.PAGE_CONTENT_NUM):
            str_cardid = self.request.get('%s%s' % (Defines.URLQUERY_CARD, i), None)
            if str_cardid and str_cardid.isdigit():
                cardidlist.append(int(str_cardid))
        str_cardid = self.request.get(Defines.URLQUERY_CARD, None)
        if str_cardid:
            str_cardidlist = str_cardid.split(',')
            cardidlist.extend([int(str_cardid) for str_cardid in str_cardidlist])
        if len(cardidlist) == 0:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        return cardidlist
