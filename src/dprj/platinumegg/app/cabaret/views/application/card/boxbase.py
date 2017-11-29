# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.cardlisthandler import CardlistHandler


class BoxHandler(CardlistHandler):
    """カードBOX.
    """
    
    def makeUrlSelf(self):
        return UrlMaker.cardbox()
    
    def writeBoxHtml(self, name):
        """HTML書き出し.
        """
        self.getViewerPlayer()
        
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
        
        # タブ切り替え用.
        url = UrlMaker.cardbox()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_CTYPE, _ctype)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_SORTBY, sortby)
        self.html_param['url_cardbox'] = self.makeAppLinkUrl(url)
        
        url = UrlMaker.sell()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_CTYPE, _ctype)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_SORTBY, sortby)
        self.html_param['url_sell'] = self.makeAppLinkUrl(url)
        
        self.saveSortParams()
        
        self.writeAppHtml(name)
