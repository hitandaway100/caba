# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.card import CardUtil
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventMaster

class Handler(BattleEventBaseHandler):
    """バトルイベントピースプレゼント(リザルトアニメーションの前に実行する)
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        model_mgr = self.getModelMgr()

        uid = self.getViewerPlayer().id
        args = self.getUrlArgs('/battleeventbattlepiecepresent/')
        eventid = args.getInt(0)
        rarity = args.getInt(1)
        piecenumber = args.getInt(2)
        is_complete = args.getInt(3)

        if is_complete:
            piecemaster_list = BackendApi.get_battleevent_piecemaster(model_mgr, eventid, using=settings.DB_READONLY)
            piece_dir = BackendApi.get_battleevent_piecemaster_instance(rarity, piecemaster_list).name
            codename = BattleEventMaster.getByKey(eventid).codename
            piece_path = 'event/btevent/%s/%s/piece_complete.png' % (codename, piece_dir)
            effectpath = 'btevent/piece_complete/effect.html'
            mid = BackendApi.get_userdata_piece_complete_prize_cardid(uid, eventid, rarity)
            master = BackendApi.get_cardmasters([mid]).get(mid)
            url = UrlMaker.battleevent_battleresult(eventid, rarity, piecenumber)
            params = {
                'backUrl': self.makeAppLinkUrl(url),
                'pre' : self.url_static_img,
                'card' : CardUtil.makeThumbnailUrlLarge(master),
                'piece' : piece_path,
                'bg' : 'event/btevent/%s/bg_piececomplete.png' % codename
            }

            self.appRedirectToEffect(effectpath, params)
        else:
            url = UrlMaker.battleevent_battleresult(eventid, rarity, piecenumber)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
def main(request):
    return Handler.run(request)
