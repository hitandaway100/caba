# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.evolution.base import EvolutionHandler
from platinumegg.app.cabaret.models.Player import PlayerGold
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
import settings_sub
from platinumegg.app.cabaret.util.card import CardUtil
from defines import Defines


class Handler(EvolutionHandler):
    """進化合成アニメ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold]
    
    def process(self):
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        # 合成結果.
        evolutiondata = BackendApi.get_evolutiondata(model_mgr, v_player.id, using=settings.DB_READONLY)
        
        # 進化後カード.
        basecardset = BackendApi.get_cards([evolutiondata.result_baseid], model_mgr, using=settings.DB_READONLY)
        if not basecardset:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'ハメ管理したキャストが見つかりません.')
            url = UrlMaker.evolution()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        basecardset = basecardset[0]
        
        # ベースカード.
        pre_master = BackendApi.get_cardmasters([evolutiondata.mid], model_mgr, using=settings.DB_READONLY).get(evolutiondata.mid)
        if pre_master is None or (pre_master.albumhklevel+1) != basecardset.master.albumhklevel:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'ハメ管理前のキャストが見つかりません.')
            url = UrlMaker.evolution()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # 素材カード.
        materialcard = BackendApi.get_cards([evolutiondata.result_materialid], model_mgr, using=settings.DB_READONLY, deleted=True)
        if not materialcard:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'ハメ管理に使用したキャストが見つかりません.')
            url = UrlMaker.evolution()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        materialcard = materialcard[0]
        
        miniImg = {}
        endText2 = None
        endText3 = None
        # 文言.
        endText = Defines.EffectTextFormat.EVOLUTION_ENDTEXT % (basecardset.master.name, basecardset.master.hklevel - 1, evolutiondata.result_takeover)
        if evolutiondata.result_flag_memories_open:
            movie = False
            memories_list = BackendApi.get_album_memories_list(self, v_player.id, basecardset.master.album, using=settings.DB_READONLY)
            
            if memories_list:
                cnt = 0
                for memories in memories_list:
                    if memories.get('cardid') != basecardset.master.id or not memories.get('is_new'):
                        continue
                    elif memories.get('contenttype') == Defines.MemoryContentType.MOVIE:
                        movie = True
                    if cnt < 2:
                        cnt += 1
                        miniImg['miniCard%d' % cnt] = memories['thumbUrl']
            
            endText2 = Defines.EffectTextFormat.EVOLUTION_ENDTEXT2 % basecardset.master.maxlevel
            
            # 思い出アルバム開放.
            if movie:
                endText3 = Defines.EffectTextFormat.EVOLUTION_ENDTEXT3_MOVIE
            else:
                endText3 = Defines.EffectTextFormat.EVOLUTION_ENDTEXT3_MEMORIES
        
        params = {
            'card1':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(pre_master)),
            'card2':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(materialcard.master)),
            'mixCard':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(basecardset.master)),
            'startText':Defines.EffectTextFormat.EVOLUTION_STARTTEXT,
            'endText':endText,
            'backUrl' : self.makeAppLinkUrl(UrlMaker.evolutionresult()),
        }
        if endText2:
            params['endText2'] = endText2
        if endText3:
            params['endText3'] = endText3
        params.update(**miniImg)
        self.appRedirectToEffect('gousei/effect.html', params)

def main(request):
    return Handler.run(request)
