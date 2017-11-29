# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.card.boxbase import BoxHandler
from defines import Defines


class Handler(BoxHandler):
    """カードBOX.
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
    
    def makeUrlSelf(self):
        return UrlMaker.cardbox()
    
    def process(self):
        
        self.loadSortParams()
        
        self.setFromPage(Defines.FromPages.CARDBOX, [self.getCtypeOri(), self.getSortby(), self.getPage()])
        
        self.putCardList()
        
        self.html_param['urlquery_add'] = Defines.URLQUERY_ADD
        self.html_param['urlquery_rem'] = Defines.URLQUERY_REM
        
        url = UrlMaker.cardprotect()
        self.html_param['url_protect'] = self.makeAppLinkUrl(url)
        
        self.writeBoxHtml('card/cardbox')

def main(request):
    return Handler.run(request)
