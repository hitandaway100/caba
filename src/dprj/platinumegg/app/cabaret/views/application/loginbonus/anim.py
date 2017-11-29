# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.views.application.loginbonus.base import LoginBonusHandler
from platinumegg.app.cabaret.models.Player import PlayerLogin
from platinumegg.lib.opensocial.util import OSAUtil
import settings
from defines import Defines
from platinumegg.app.cabaret.util.rediscache import LoginBonusAnimationSet,\
    TotalLoginBonusAnimationSet


class Handler(LoginBonusHandler):
    """ログインボーナス演出.
    ・連続ログインの場合.
        演出は最大で12日分表示される.
            12日より少ない場合.
                空白にする.
            12日より多い場合.
                12日以内は通常通り.
                13日以降は次の行を表示して古い行を見えなくする?.
            歯抜けは想定しない.
            データが悪いってことでエラーにしてもいいらしい.
    ・累計ログインの場合.
        基本的に連続ログインと同じ.
        報酬の文言にアクセスボーナスも加えないといけない.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerLogin]
    
    def process(self):
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        if not BackendApi.check_loginbonus_received(v_player.getModel(PlayerLogin), OSAUtil.get_now()):
            # まだ受け取っていない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'まだ受け取っていない')
            url = self.makeAppLinkUrlRedirect(UrlMaker.loginbonus())
            self.appRedirect(url)
            return
        
        model_mgr = self.getModelMgr()
        
        # ログインボーナス設定.
        config = BackendApi.get_current_totalloginbonusconfig(model_mgr, using=settings.DB_READONLY)
        totallogin_mid = config.getCurrentMasterID(v_player.lbtime)
        totalloginmaster = BackendApi.get_loginbonustimelimitedmaster(model_mgr, totallogin_mid, using=settings.DB_READONLY)
        
        if totalloginmaster:
            tldays = v_player.tldays
            
            table = BackendApi.get_loginbonustimelimiteddaysmaster_day_table_by_timelimitedmid(model_mgr, totallogin_mid, using=settings.DB_READONLY)
            loginbonuslist = BackendApi.get_loginbonustimelimiteddaysmaster_by_idlist(model_mgr, table.values(), using=settings.DB_READONLY)
            daylist = table.keys()
            daylist.sort()
            daymax = daylist[-1] if daylist else 0
            
            # 受け取ったログインボーナス.
            loginbonus = BackendApi.get_loginbonustimelimiteddaysmaster(model_mgr, totallogin_mid, tldays, using=settings.DB_READONLY)
            # 次の日のボーナス.
            tomorrowbonus = BackendApi.get_loginbonustimelimiteddaysmaster(model_mgr, totallogin_mid, (tldays % daymax) + 1, using=settings.DB_READONLY)
            
            accessbonuslist = BackendApi.get_accessbonus_list(model_mgr, v_player.pdays, using=settings.DB_READONLY)
            
            params = self.makeEffectParams(v_player.tldays, loginbonuslist, loginbonus, tomorrowbonus, col_num=5, pre=True)
            params.update({
                'text1' : Defines.EffectTextFormat.TOTALLOGINBONUS_TEXT1 % tldays,
                'text2' : Defines.EffectTextFormat.TOTALLOGINBONUS_TEXT2 % self.getTotalBonusItemText(loginbonus, accessbonuslist),
                'text3' : Defines.EffectTextFormat.TOTALLOGINBONUS_TEXT3 % self.getTotalBonusItemText(tomorrowbonus, accessbonuslist),
            })
            effectname = 'loginstamp2'
        elif not config.continuity_login:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return
        else:
            # 連続ログイン日数.
            ldays = v_player.ldays
            
            # 受け取ったログインボーナス.
            loginbonus = BackendApi.get_continuityloginbonus(model_mgr, ldays, using=settings.DB_READONLY)
            # 次の日のボーナス.
            tomorrowbonus = BackendApi.get_continuityloginbonus(model_mgr, ldays + 1, using=settings.DB_READONLY)
            
            # 連続ログイン報酬.
            loginbonuslist = BackendApi.get_continuityloginbonus_all(model_mgr, using=settings.DB_READONLY)
            
            params = self.makeEffectParams(ldays, loginbonuslist, loginbonus, tomorrowbonus)
            params.update({
                'text1' : Defines.EffectTextFormat.LOGINBONUS_TEXT1 % ldays,
                'text2' : Defines.EffectTextFormat.LOGINBONUS_TEXT2 % self.getBonusItemText(loginbonus),
                'text3' : Defines.EffectTextFormat.LOGINBONUS_TEXT3 % self.getBonusItemText(tomorrowbonus),
            })
            effectname = 'login'
        
        # 遷移先.
        if BackendApi.check_raidevent_lead_opening(model_mgr, v_player.id, using=settings.DB_READONLY):
            # イベントOPを見ないといけない.
            url = UrlMaker.raidevent_opening()
        elif BackendApi.check_raidevent_lead_bigboss(model_mgr, v_player.id, using=settings.DB_READONLY):
            # 大ボス演出を見ないといけない.
            url = UrlMaker.raidevent_bigboss()
        elif BackendApi.check_raidevent_lead_epilogue(model_mgr, v_player.id, using=settings.DB_READONLY):
            # イベントEDを見ないといけない.
            url = UrlMaker.raidevent_epilogue()
        elif BackendApi.check_scoutevent_lead_opening(model_mgr, v_player.id, using=settings.DB_READONLY):
            # イベントOPを見ないといけない.
            url = UrlMaker.scoutevent_opening()
        elif BackendApi.check_scoutevent_lead_epilogue(model_mgr, v_player.id, using=settings.DB_READONLY):
            # イベントEDを見ないといけない.
            url = UrlMaker.scoutevent_epilogue()
        elif BackendApi.check_battleevent_lead_opening(model_mgr, v_player.id, using=settings.DB_READONLY):
            # イベントOPを見ないといけない.
            url = UrlMaker.battleevent_opening()
        elif not BackendApi.check_battleevent_loginbonus_received(model_mgr, v_player.id, using=settings.DB_READONLY, now=OSAUtil.get_now()):
            # イベントログインボーナスを受け取らないといけない.
            url = UrlMaker.battleevent_loginbonus()
        elif BackendApi.check_battleevent_lead_epilogue(model_mgr, v_player.id, using=settings.DB_READONLY):
            # イベントエピローグを見ないといけない.
            url = UrlMaker.battleevent_epilogue()
        else:
            url = UrlMaker.present()
        params['backUrl'] = self.makeAppLinkUrlSwfEmbed(url)
        
        self.appRedirectToEffect('%s/effect.html' % effectname, params)
    
    def makeEffectParams(self, ldays, loginbonuslist, loginbonus, tomorrowbonus, col_num=4, row_num=3, pre=False):
        params = {}
        
        # 演出の行と列の数.
        COL_NUM = col_num
        ROW_NUM = row_num
        CONTENT_NUM_MAX = COL_NUM * ROW_NUM
        
        loginbonuslist.sort(key=lambda x:x.day)
        
        # 表示する日.
        lday_max = loginbonuslist[-1].day if loginbonuslist else 0
        if lday_max <= CONTENT_NUM_MAX:
            start = min(1, lday_max)
            end = lday_max
        else:
            end = min(lday_max, max(CONTENT_NUM_MAX, int((ldays + COL_NUM - 1) / COL_NUM) * COL_NUM))
            start = max(1, min(end - CONTENT_NUM_MAX + 1, lday_max))
        
        stampNum = 0
        itemPosition = []
        
        if pre:
            params['pre'] = self.url_static_img
        
        for lday in xrange(start, end + 1):
            idx = lday - 1
            master = loginbonuslist[idx]
            number = lday - start + 1
            
            if lday != master.day:
                # マスターデータに抜けがある.
                raise CabaretError(u'ログインボーナスが足りません', CabaretError.Code.INVALID_MASTERDATA)
            elif master.day == loginbonus.day:
                # 受け取ったボーナス.
                stampNum = number
            
            # サムネイル.
            params['itemImage%d' % number] = master.thumb if pre else self.makeAppLinkUrlImg(master.thumb)
            itemPosition.append(str(number))
        
        params['stampNum'] = stampNum
        params['itemPosition'] = Defines.ANIMATION_SEPARATE_STRING.join(itemPosition)
        return params
    
    def getBonusItemText(self, master, *args):
        """ログインボーナスのテキストを作成
        """
        if LoginBonusAnimationSet.exists(master.day):
            items = LoginBonusAnimationSet.get(master.day)
        else:
            model_mgr = self.getModelMgr()
            prizelist = BackendApi.get_prizelist(model_mgr, master.prizes, using=settings.DB_READONLY)
            prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
            items = [listitem['text'] for listitem in prizeinfo['listitem_list']]
            LoginBonusAnimationSet.save(master.day, items)
        return Defines.STR_AND.join(items)
    
    def getTotalBonusItemText(self, master, accessbonuslist):
        """累計ログインボーナスのテキストを作成
        """
        if TotalLoginBonusAnimationSet.exists(master.mid, master.day):
            items = TotalLoginBonusAnimationSet.get(master.mid, master.day)
        else:
            model_mgr = self.getModelMgr()
            prizeidlist = master.prizes[:]
            for accessbonus in accessbonuslist:
                prizeidlist.extend(accessbonus.prizes)
            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=settings.DB_READONLY)
            prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
            items = [listitem['text'] for listitem in prizeinfo['listitem_list']]
            TotalLoginBonusAnimationSet.save(master.mid, master.day, items)
        return Defines.STR_AND.join(items)
    

def main(request):
    return Handler.run(request)
