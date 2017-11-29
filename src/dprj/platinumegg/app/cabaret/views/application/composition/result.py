# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.composition.base import CompositionHandler
from platinumegg.app.cabaret.models.Player import PlayerGold
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
import settings_sub
from platinumegg.app.cabaret.util.card import CardUtil


class Handler(CompositionHandler):
    """合成アニメ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold]
    
    def process(self):
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        # 合成結果.
        compositiondata = BackendApi.get_compositiondata(model_mgr, v_player.id, using=settings.DB_READONLY)
        
        # ベースカード.
        basecardset = BackendApi.get_cards([compositiondata.result_baseid], model_mgr, using=settings.DB_READONLY)
        if not basecardset or basecardset[0].card.mid != compositiondata.mid:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'教育したキャストが見つかりません.')
            url = UrlMaker.composition()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        basecardset = basecardset[0]
        
        self.html_param['basecard_post'] = Objects.card(self, basecardset)
        compositiondata.set_to_card(basecardset.card)
        self.html_param['basecard_pre'] = Objects.card(self, basecardset)
        
        # 素材カード.
        materialcardsetlist = BackendApi.get_cards(compositiondata.result_materialidlist, model_mgr, using=settings.DB_READONLY, deleted=True)
        self.html_param['cardlist'] = [Objects.card(self, cardset) for cardset in materialcardsetlist]
        
        # 経験値とレベル.
        self.html_param['exp'] = compositiondata.result_exp
        self.html_param['levelup'] = compositiondata.result_lvup
        
        # お金.
        self.html_param['cost'] = compositiondata.result_cost_gold
        
        # スキル.
        self.html_param['skilllevelup'] = compositiondata.result_skilllvup
        
        # 成功 or 大成功.
        self.html_param['is_great_success'] = compositiondata.result_flag_great_success
        
        # 上昇値.
        level_pre = compositiondata.result_lvpre
        level_add = compositiondata.result_lvup
        power_add = 0
        if 0 < level_add:
            basemaster = basecardset.master
            pow_pre = CardUtil.calcPower(basemaster.gtype, basemaster.basepower, basemaster.maxpower, level_pre, basemaster.maxlevel, basecardset.card.takeover)
            pow_post = CardUtil.calcPower(basemaster.gtype, basemaster.basepower, basemaster.maxpower, level_pre + level_add, basemaster.maxlevel, basecardset.card.takeover)
            power_add = pow_post - pow_pre
        self.html_param['power_add'] = power_add
        self.html_param['level_add'] = level_add
        self.html_param['skilllevel_add'] = compositiondata.result_skilllvup
        
        # 続けて合成のURL.
        url = UrlMaker.compositionmaterial(basecardset.id)
        self.html_param['url_continue'] = self.makeAppLinkUrl(url)
        
        self.writeAppHtml('composition/complete')

def main(request):
    return Handler.run(request)
