# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.composition.base import CompositionHandler
from platinumegg.app.cabaret.models.Player import PlayerGold
from platinumegg.app.cabaret.util.api import Objects, BackendApi
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from platinumegg.app.cabaret.util.card import CardListFilter
from defines import Defines


class Handler(CompositionHandler):
    """合成素材カード選択.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold]
    
    @classmethod
    def getCacheNameSpaceBase(self):
        return 'composition:material:%s'
    
    def __getCardlist(self, model_mgr, uid):
        if self.__cardlist is None:
            ctype = self.getCtype()
            sortby = self.getSortby()
            ckind = self.getCKindList()
            maxrare = self.getMaxRare()
            
            filter_obj = CardListFilter(ctype=ctype, maxrare=maxrare, ckind=ckind)
            skillmaster = self.__basecard.master.getSkill()
            if skillmaster:
                # 同じスキルのみの絞り込み.
                skillid = self.getSkillId()
                post_skillmaster = None
                if skillid:
                    post_skillmaster = BackendApi.get_skillmaster(model_mgr, skillid, using=settings.DB_READONLY)
                if post_skillmaster and post_skillmaster.id == skillmaster.id:
                    filter_func = lambda x,y,sk:y.getSkillGroup() == sk
                    filter_obj.add_optional_filter(filter_func, post_skillmaster.group)
            else:
                # スキルレベルをあげる素材はいらない.
                filter_func = lambda x,y:y.ckind != Defines.CardKind.SKILL
                filter_obj.add_optional_filter(filter_func)
            self.__cardlist = BackendApi.get_compositionmaterial_list(uid, self.__basecard, filter_obj=filter_obj, sortby=sortby, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
        return self.__cardlist
    
    def getCardlist(self, model_mgr, uid, offset, limit):
        return self.__getCardlist(model_mgr, uid)[offset:(offset+limit)]
    
    def getCardPageNumMax(self, model_mgr, uid):
        num = len(self.__getCardlist(model_mgr, uid))
        page = max(1, int((num + self.PAGE_CONTENT_NUM - 1) / self.PAGE_CONTENT_NUM))
        return page
    
    def makeUrlSelf(self):
        return UrlMaker.compositionmaterial(self.__baseid)
    
    def process(self):
        self.__cardlist = None
        
        args = self.getUrlArgs('/compositionmaterial/')
        try:
            self.__baseid = int(args.get(0))
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
        self.__basecard = basecard
        
        self.loadSortParams(default_sortby=Defines.CardSortType.RARE, default_ckind_type=Defines.CardKind.ListFilterType.ALL_KIND)
        
        # プレイヤー情報.
        self.html_param['player'] = Objects.player(self, v_player)
        
        # カード所持数.
        cardnum = BackendApi.get_cardnum(v_player.id, model_mgr, using=settings.DB_READONLY)
        self.html_param['cardnum'] = cardnum
        
        # カード.
        self.putCardList()
        
        # 確認ページのUrl.
        url = UrlMaker.compositionyesno(self.__baseid)
        self.html_param['url_yesno'] = self.makeAppLinkUrl(url)
        
        self.writeCompositionHtml('composition/materialselect')

def main(request):
    return Handler.run(request)
