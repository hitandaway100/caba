# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.produce_event.base import ProduceEventBaseHandler
import urllib
from defines import Defines
import settings_sub
from platinumegg.app.cabaret.util.happening import HappeningUtil


class Handler(ProduceEventBaseHandler):
    """スカウト結果.
    引数:
        実行したスカウトのID.
        確認キー.
        結果のindex.
    """

    @classmethod
    def getViewerPlayerClassList(cls):
        return []

    def process(self):
        self.__swf_params = {}

        args = self.getUrlArgs('/produceeventscoutresultanim/')
        try:
            stageid = int(args.get(0))
            scoutkey = urllib.unquote(args.get(1))
            index = int(args.get(2) or 0)
        except:
            raise CabaretError(u'引数が不正です', CabaretError.Code.ILLEGAL_ARGS)

        v_player = self.getViewerPlayer()
        uid = v_player.id

        model_mgr = self.getModelMgr()

        using = settings.DB_READONLY

        flag_skip = BackendApi.get_scoutskip_flag(uid)

        eventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=using)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        mid = eventmaster.id

        # 進行情報
        playdata = BackendApi.get_produceeventstage_playdata(model_mgr, mid, uid, using=using)
        if playdata and playdata.confirmkey == scoutkey:
            # DBからとり直す
            playdata = BackendApi.get_produceeventstage_playdata(model_mgr, mid, uid, using=using, reflesh=True)
            if playdata and playdata.alreadykey != scoutkey:
                if settings_sub.IS_LOCAL:
                    raise CabaretError(u'キーが正しくありません %s vd %s' % (playdata.alreadykey if playdata else 'None', scoutkey))
                url = self.makeAppLinkUrlRedirect(UrlMaker.produceevent_top())
                self.appRedirect(url)
                return

        eventlist = playdata.result.get('event', [])[index:]
        if not eventlist:
            raise CabaretError(u'引数が不正です', CabaretError.Code.ILLEGAL_ARGS)

        table = {
            Defines.ScoutEventType.COMPLETE: (self.procComplete, False),
            Defines.ScoutEventType.LEVELUP: (self.procLevelup,True),
            Defines.ScoutEventType.HAPPENING: (self.procHappening, True),
        }

        proc = None
        next_event = None
        for idx, event in enumerate(eventlist):
            next_event = eventlist[idx + 1] if (idx +1) < len(eventlist) else None
            tmp = table.get(event.get_type(), None)
            if tmp is None:
                index += idx
                break
            tmp_proc, is_skipok = tmp
            if flag_skip and is_skipok:
                continue
            index += idx
            proc = tmp_proc
            break

        if not proc:
            url = UrlMaker.produceevent_scoutresult(stageid, scoutkey)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return

        if next_event and table.has_key(next_event.get_type()):
            url = UrlMaker.produceevent_scoutresultanim(stageid, scoutkey, index+1)
        else:
            url = UrlMaker.produceevent_scoutresult(stageid, scoutkey)

        self.__swf_params['backUrl'] = self.makeAppLinkUrl(url)

        self.__playdata = playdata
        proc(event)

    def procComplete(self, event):
        """スカウト完了演出.
        """
        self.__swf_params['text'] = Defines.EffectTextFormat.SCOUTRESULT_COMPLETE_TEXT
        self.appRedirectToEffect('scoutclear/effect.html', self.__swf_params)

    def procLevelup(self, event):
        """レベルアップ演出.
        """
        resulttexts = []

        # レベル情報.
        resulttexts.append(Defines.EffectTextFormat.LEVELUP_STATUSTEXT % event.level)

        self.__swf_params['statusText'] = u'\n'.join(resulttexts)

        self.appRedirectToEffect('levelup/effect.html', self.__swf_params)

    def procHappening(self, event):
        """ハプニング発生演出.
        """
        using = self.__playdata.current_db

        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()


        happeningid = BackendApi.get_current_producehappeningid(model_mgr, v_player.id, using=using, reflesh=True)
        happeningset = BackendApi.get_producehappening(model_mgr, happeningid, using=using)
        if happeningset:
            eventid = HappeningUtil.get_produceeventid(happeningset.happening.event)
            if eventid:
                eventmaster = BackendApi.get_produce_event_master(model_mgr, eventid, using=settings.DB_READONLY)
                if eventmaster:
                    raidboss = BackendApi.get_raid(model_mgr, happeningid, using=using)
                    if raidboss:
                        BackendApi.reset_raidboss_eventraidmaster(model_mgr, raidboss, happeningset.happening.event, using=settings.DB_READONLY)
                        self.__swf_params['pre'] = '%s%s/' % (self.url_static_img, raidboss.master.thumb)
                        if raidboss.is_produceevent_bigboss():
                            # Redirect to chohutokyaku effect
                            self.appRedirectToEffect('produce_event/produce_chohutokyaku/effect.html', self.__swf_params)
                        else:
                            # Redirect to hutokyaku effect
                            self.appRedirectToEffect('produce_event/produce_hutokyaku/effect.html', self.__swf_params)
                        return
        self.appRedirectToEffect('chohutokyaku/effect.html', self.__swf_params)

def main(request):
    return Handler.run(request)
