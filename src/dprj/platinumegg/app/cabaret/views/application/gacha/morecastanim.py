# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerGachaPt, PlayerRequest
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.app.cabaret.models.Card import CardMaster
from defines import Defines
from platinumegg.app.cabaret.util.card import CardUtil
from platinumegg.app.cabaret.util.gacha import GachaUtil
from platinumegg.lib.pljson import Json
import settings
from platinumegg.app.cabaret.util.api import BackendApi

class Handler(GachaHandler):


  @classmethod
  def getViewerPlayerClassList(cls):
    return [PlayerGachaPt, PlayerRequest]

  def process(self):
    url_args = self.getUrlArgs('/gachamorecast/')
    model_mgr = self.getModelMgr()
    mid = int(url_args.get(0))
    self.set_masterid(mid)

    v_player = self.getViewerPlayer()
    gachamaster = self.getGachaMaster()
    
    effectpath = 'gachamorecast/effect2.html'
    dataUrl = self.makeAppLinkUrlEffectParamGet(GachaUtil.makeGachaDataUrl(v_player, gachamaster, morecast=1))
    self.appRedirectToEffect2(effectpath, dataUrl)

def main(request):
  return Handler.run(request)
