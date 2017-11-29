# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.composition.base import CompositionHandler
from platinumegg.app.cabaret.models.Player import PlayerGold
from platinumegg.app.cabaret.util.api import Objects, BackendApi
import settings
from defines import Defines


class Handler(CompositionHandler):
    """合成ベースカード選択.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold]
    
    @classmethod
    def getCacheNameSpaceBase(self):
        return 'composition:base:%s'
    
    def makeUrlSelf(self):
        return UrlMaker.composition()
    
    def __getCardlistAll(self, model_mgr, uid):
        if self.__cardlist_all is None:
            sortby = self.getSortby()
            self.__cardlist_all = BackendApi.get_compositionbase_list(uid, sortby=sortby, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
        return self.__cardlist_all
    
    def __getCardlist(self, model_mgr, uid):
        if self.__cardlist is None:
            ctype = self.getCtype()
            if ctype and ctype != Defines.CharacterType.ALL:
                self.__cardlist = [card for card in self.__getCardlistAll(model_mgr, uid) if card.master.ctype == ctype]
            else:
                self.__cardlist = self.__getCardlistAll(model_mgr, uid)
        return self.__cardlist
    
    def __getSkillCardlist(self, model_mgr, uid):
        if self.__filtered_by_skill_cardlist is None:
            skillid = self.getSkillId()
            cardlist = self.__getCardlist(model_mgr, uid)
            if skillid:
                self.__filtered_by_skill_cardlist = [card for card in cardlist if card.master.skill == skillid]
            else:
                self.__filtered_by_skill_cardlist = cardlist
        return self.__filtered_by_skill_cardlist
    
    def getCardlist(self, model_mgr, uid, offset, limit):
        return self.__getSkillCardlist(model_mgr, uid)[offset:(offset+limit)]
    
    def getCardPageNumMax(self, model_mgr, uid):
        num = len(self.__getSkillCardlist(model_mgr, uid))
        page = max(1, int((num + self.PAGE_CONTENT_NUM - 1) / self.PAGE_CONTENT_NUM))
        return page
    
    def getSkillMasterList(self):
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        cardlist = self.__getCardlistAll(model_mgr, v_player.id)
        skilllist = list(set([card.master.getSkill() for card in cardlist if card.master.skill]))
        skilllist.sort(key=lambda x:x.id)
        return skilllist
    
    def process(self):
        
        self.__cardlist_all = None
        self.__cardlist = None
        self.__filtered_by_skill_cardlist = None
        self.__skilllist = None
        
        model_mgr = self.getModelMgr()
        
        self.loadSortParams()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        self.html_param['player'] = Objects.player(self, v_player)
        
        # カード所持数.
        cardnum = BackendApi.get_cardnum(v_player.id, model_mgr, using=settings.DB_READONLY)
        self.html_param['cardnum'] = cardnum
        
        # カード.
        self.putCardList()
        
        # スキル一覧.
        skilllist = self.getSkillMasterList()
        self.html_param['skillmasterlist'] = [Objects.skillmaster(skill) for skill in skilllist]
        
        self.writeCompositionHtml('composition/baseselect')

def main(request):
    return Handler.run(request)
