# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerRegist, PlayerTutorial, PlayerExp
from platinumegg.app.cabaret.models.LevelUpBonus import LevelUpBonusMaster, LevelUpBonusPlayerData
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.card import CardSet
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
import settings
from defines import Defines

class Handler(AppHandler):
    """レベルアップ達成ボーナス.
    """

    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerExp]

    def process(self):
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()

        self.html_param['header_banner'] = 'banner/lvup_bonus/lvup_bonus02/lvup_bonus02_header.png'
        self.html_param['missions'] = self._items(model_mgr, v_player)
        self.html_param['rule'] = ''
        self.html_param['scoutpage'] = self.makeAppLinkUrl(UrlMaker.scout())
        self.writeAppHtml('levelupbonus')

    def _items(self, model_mgr, v_player):
        key = LevelUpBonusPlayerData.makeID(self.getViewerPlayer().id, Defines.LEVELUP_BONUS_VERSION)
        key = LevelUpBonusPlayerData.makeID(v_player.id, Defines.LEVELUP_BONUS_VERSION)
        playerdata = model_mgr.get_model(LevelUpBonusPlayerData, key)
        if playerdata is None:
            playerdata = LevelUpBonusPlayerData.createInstance(key)

        return BackendApi.get_levelupbonus_data(self, model_mgr, playerdata.last_prize_level, Defines.LEVELUP_BONUS_VERSION, using=settings.DB_READONLY)

def main(request):
    return Handler.run(request)
