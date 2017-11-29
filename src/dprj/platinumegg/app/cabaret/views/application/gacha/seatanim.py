# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerGachaPt, PlayerRequest
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import urllib
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
import settings
from platinumegg.app.cabaret.util.present import PrizeData, PresentSet


class Handler(GachaHandler):
    """引抜実行アニメ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGachaPt, PlayerRequest]
    
    def process(self):
        args = self.getUrlArgs('/gachaseatanim/')
        try:
            mid = int(args.get(0))
            key = urllib.unquote(args.get(1))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        self.set_masterid(mid)
        
        v_player = self.getViewerPlayer()
        if v_player.req_alreadykey != key:
            # 結果が見当たらない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'結果アニメを出せない')
            url = UrlMaker.gacha()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        uid = v_player.id
        
        model_mgr = self.getModelMgr()
        
        seatmodels = self.getSeatModels(True)
        seatmaster = seatmodels.get('seatmaster')
        seatplaycount = seatmodels.get('playcount')
        seatplaydata = seatmodels.get('playdata')
        gachamaster = BackendApi.get_gachamaster(model_mgr, mid)

        tableid = gachamaster.seattableid
        tablemaster = None
        if tableid:
            tablemaster = BackendApi.get_gachaseattablemaster(model_mgr, tableid, using=settings.DB_DEFAULT)

        def _get_playdata(mid):
            return BackendApi.get_gachaseatplaydata(model_mgr, uid, [mid], get_instance=True, using=settings.DB_DEFAULT).get(mid)

        if seatplaydata.is_first() and 0 < seatplaycount.lap:
            oldlap_mid = tablemaster.getSeatId(seatplaycount.lap)
            seatmaster = BackendApi.get_gachaseatmaster(model_mgr, oldlap_mid, using=settings.DB_DEFAULT)
            seatplaydata = _get_playdata(oldlap_mid)

        if seatmaster is None or seatplaydata is None or seatplaycount is None:
            # シートの演出を表示できない結果が見当たらない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'結果アニメを出せない')
            url = UrlMaker.gacha()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        params = {
            'prefix' : self.url_static_img,
        }
        
        # 表示するアイテムの画像URL.
        flags = {}
        prize_map = {}
        idx = 0
        allempty = True
        allend = True
        
        while True:
            prizeid = seatmaster.getPrizeId(idx)
            if prizeid is None:
                break
            weight = seatmaster.getWeight(idx)
            if prizeid and weight:
                if seatplaydata.getFlag(idx):
                    allempty = False
                    flags[idx] = True
                else:
                    allend = False
                    flags[idx] = False
                prize_map[prizeid] = None
            idx += 1
        
        if allempty and 0 < seatplaycount.lap:
            allend = True
        
        for prizemaster in BackendApi.get_prizemaster_list(model_mgr, prize_map.keys(), using=settings.DB_READONLY):
            prize_map[prizemaster.id] = PrizeData.createByMaster(prizemaster)

        for i in xrange(idx):
            flag = flags.get(i, None)
            if flag is None:
                continue
            
            prizeid = seatmaster.getPrizeId(i)
            prize = prize_map.get(prizeid)
            if not prize:
                continue
            
            thumb = seatmaster.getThumb(i)
            
            if not thumb:
                presentlist = BackendApi.create_present_by_prize(model_mgr, uid, [prize], 0, using=settings.DB_READONLY, do_set_save=False)
                if not presentlist:
                    continue
                
                presentlist = presentlist[:1]
                presentset = PresentSet.presentToPresentSet(model_mgr, presentlist, using=settings.DB_READONLY)[0]
                thumb = presentset.itemthumbnail_rect_middle
            
            params['i%02d' % i] = thumb
            params['f%02d' % i] = 1 if (allend or flag) and i != seatplaydata.last else 0
        
        # 選択されたアイテムのindex.
        if params.get('i%02d' % seatplaydata.last) is None:
            # シートの演出を表示できない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'結果が存在しない')
            url = UrlMaker.gacha()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        params['idx'] = seatplaydata.last
        
        # ロゴ画像.
        params['logoPre'] = self.makeAppLinkUrlImg(seatmaster.img_effect)
        
        # 遷移先.
        url = UrlMaker.gacharesult(self.gachamaster_id, v_player.req_alreadykey)
        params['backUrl'] = self.makeAppLinkUrl(url)
        
        self.appRedirectToEffect('%s/effect.html' % seatmaster.effectname, params)
    

def main(request):
    return Handler.run(request)
