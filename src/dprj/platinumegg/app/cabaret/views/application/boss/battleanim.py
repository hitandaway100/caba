# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.boss.base import BossHandler
import settings_sub
from platinumegg.app.cabaret.util.api import BackendApi
import urllib
import settings


class Handler(BossHandler):
    """ボス戦アニメーション.
    表示するもの:
        ボス情報.
        デッキ情報.
        ボス戦の結果
    引数:
        エリアID.
        キー.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        args = self.getUrlArgs('/bossbattleanim/')
        try:
            # エリア.
            areaid = int(args.get(0, None))
            self.setAreaID(areaid)
            battlekey = urllib.unquote(args.get(1))[:32]
            if not battlekey:
                raise
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        using = settings.DB_READONLY
        
        # 結果.
        bossbattle = BackendApi.get_bossresult(model_mgr, uid, areaid, using=using)
        if bossbattle is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'結果が見つかりませんでした', CabaretError.Code.ILLEGAL_ARGS)
            self.callFunctionByFromPage('redirectToScoutTop')
            return
        
        
        # 演出用パラメータ.
        boss = self.getBossMaster()
        animdata = bossbattle.anim
        params = BackendApi.make_bossbattle_animation_params(self, animdata, boss.thumb)
        
        # ボス戦結果へのURL.
        params['backUrl'] = self.callFunctionByFromPage('getEffectBackUrl', bossbattle, battlekey)
        
        self.appRedirectToEffect('bossbattle2/effect.html', params)
    
    #==================================================
    # 通常スカウト.
    def getEffectBackUrl_SCOUT(self, bossbattle, battlekey):
        area = self.getAreaMaster()
        areaid = area.id
        backUrl = self.makeAppLinkUrl(UrlMaker.bossresult(areaid, battlekey))
        return backUrl
    
    #==================================================
    # スカウトイベント.
    def getEffectBackUrl_SCOUTEVENT(self, bossbattle, battlekey):
        area = self.getAreaMaster()
        areaid = area.id
        if area.bossscenario and bossbattle.anim.winFlag:
            backUrl = self.makeAppLinkUrl(UrlMaker.scouteventscenarioanim(areaid, battlekey))
        else:
            backUrl = self.makeAppLinkUrl(UrlMaker.bossresult(areaid, battlekey))
        return backUrl
    
    #==================================================
    # レイドイベント.
    def getEffectBackUrl_RAIDEVENTSCOUT(self, bossbattle, battlekey):
        area = self.getAreaMaster()
        areaid = area.id
        if area.bossscenario and bossbattle.anim.winFlag:
            backUrl = self.makeAppLinkUrl(UrlMaker.raidevent_scenarioanim(areaid, battlekey))
        else:
            backUrl = self.makeAppLinkUrl(UrlMaker.bossresult(areaid, battlekey))
        return backUrl

    #==================================================
    # プロデュースイベント
    def getEffectBackUrl_PRODUCEEVENT(self, bossbattle, battlekey):
        return self.getEffectBackUrl_PRODUCEEVENTSCOUT(bossbattle, battlekey)

    def getEffectBackUrl_PRODUCEEVENTSCOUT(self, bossbattle, battlekey):
        area = self.getAreaMaster()
        areaid = area.id
        if area.bossscenario and bossbattle.anim.winFlag:
            backUrl = self.makeAppLinkUrl(UrlMaker.produceevent_scenarioanim(areaid, battlekey))
        else:
            backUrl = self.makeAppLinkUrl(UrlMaker.bossresult(areaid, battlekey))
        return backUrl


def main(request):
    return Handler.run(request)
