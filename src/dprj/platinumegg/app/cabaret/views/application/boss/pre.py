# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.boss.base import BossHandler
import settings_sub
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerRequest


class Handler(BossHandler):
    """ボス戦開始ページ.
    表示するもの:
        ボス情報.
        デッキのカード.
        総接客力.
        ボス戦書き込みへのURL.
    引数:
        エリアID.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRequest]
    
    def process(self):
        args = self.getUrlArgs('/bosspre/')
        try:
            # エリア.
            areaid = int(args.get(0, None))
            self.setAreaID(areaid)
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        using = settings.DB_READONLY
        
        # ボス情報.
        boss = self.getBossMaster()
        if boss is None or not self.checkBossBattleAble(model_mgr, using=using):
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'まだこの街の太客には接客できません', CabaretError.Code.ILLEGAL_ARGS)
            self.callFunctionByFromPage('redirectToScoutTop')
            return
        
        # ボス情報埋め込み.
        self.html_param['boss'] = self.makeBossObj(boss)
        
        # エリア.
        areamaster = self.getAreaMaster()
        obj_area = self.makeAreaObj(areamaster, None)
        obj_area['name'] = getattr(areamaster, 'areaname', obj_area['name'])
        self.html_param['area'] = obj_area
        
        # デッキのカード.
        self.putDeckInfoParams()
        
        # ボス戦書き込みへのURL.
        url = UrlMaker.bossbattle(areaid, v_player.req_confirmkey)
        self.html_param['url_bossbattle'] = self.makeAppLinkUrl(url)
        
        # その他リンク.
        self.callFunctionByFromPage('putLinkUrl')
        
        self.writeAppHtml('boss/bosspre')
    
    #==================================================
    # 通常スカウト.
    def putLinkUrl_SCOUT(self):
        areamaster = self.getAreaMaster()
        # デッキ変更URL.
        self.setFromPage(Defines.FromPages.BOSS, areamaster.id)
        self.html_param['url_deck'] = self.makeAppLinkUrl(UrlMaker.deck())
    
    #==================================================
    # スカウトイベント.
    def putLinkUrl_SCOUTEVENT(self):
        # イベントトップ.
        self.html_param['url_scoutevent_top'] = self.makeAppLinkUrl(UrlMaker.scoutevent_top())
        
        areamaster = self.getAreaMaster()
        # デッキ変更URL.
        self.setFromPage(Defines.FromPages.SCOUTEVENTBOSS, areamaster.id)
        self.html_param['url_deck'] = self.makeAppLinkUrl(UrlMaker.deck())
    
    #==================================================
    # レイドイベント.
    def putLinkUrl_RAIDEVENTSCOUT(self):
        areamaster = self.getAreaMaster()
        # デッキ変更URL.
        self.setFromPage(Defines.FromPages.RAIDEVENTSCOUTBOSS, areamaster.id)
        self.html_param['url_deck'] = self.makeAppLinkUrl(UrlMaker.deck())
        
        # イベントトップ.
        self.html_param['url_raidevent_top'] = self.makeAppLinkUrl(UrlMaker.raidevent_top())

    # ==================================================
    # プロデュースイベント
    def putLinkUrl_PRODUCEEVENT(self):
        return self.putLinkUrl_PRODUCEEVENTSCOUT()

    def putLinkUrl_PRODUCEEVENTSCOUT(self):
        areamaster = self.getAreaMaster()
        # デッキ変更URL
        self.setFromPage(Defines.FromPages.PRODUCEEVENTSCOUTBOSS, areamaster.id)
        self.html_param['url_deck'] = self.makeAppLinkUrl(UrlMaker.deck())

        # イベントトップ
        self.html_param['url_produceevent_top'] = self.makeAppLinkUrl(UrlMaker.produceevent_top())


def main(request):
    return Handler.run(request)
