# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.models.Gacha import GachaMaster
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.alert import AlertCode
from defines import Defines
from collections import OrderedDict

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class Handler(AdminHandler):
    """ガチャのシミュレータ.
    """

    def process(self):
        if self.request.method == "POST":
            self.procPost()

        model_mgr = self.getModelMgr()
        gachamaster_list = model_mgr.get_mastermodel_all(GachaMaster, order_by='-id', using=backup_db)
        gachamaster_list = [gachamaster for gachamaster in gachamaster_list
                            if gachamaster.consumetype == Defines.GachaConsumeType.OMAKE]

        self.html_param['gachamaster_list'] = gachamaster_list
        self.writeAppHtml('/simulator/omake_simulator')

    def procPost(self):
        """パラメータを受け取ってガチャ情報を用意する.
        """
        model_mgr = self.getModelMgr()

        # ガチャのマスターID.
        strmid = str(self.request.get('_mid') or self.request.get('_strmid')) or 0
        gachamaster = None
        if strmid.isdigit():
            mid = int(strmid)
            gachamaster = BackendApi.get_gachamaster(model_mgr, mid, using=backup_db)

        if gachamaster is None:
            self.putAlertToHtmlParam(u'存在しないガチャです.%s' % strmid, AlertCode.ERROR)
            return

        self.html_param['cur_gachamaster'] = gachamaster

        # 試験回数.
        strcnt = str(self.request.get('_cnt') or 0)
        cnt = 0
        if strcnt.isdigit():
            cnt = int(strcnt)
        if cnt < 1:
            self.putAlertToHtmlParam(u'試験回数は自然数で指定してください.', AlertCode.ERROR)
            return

        cnt = min(1000000, cnt)
        self.html_param['cnt'] = cnt

        # 試験.
        self.__testOmake(gachamaster, cnt)

    def __testOmake(self, gachamaster, cnt):
        """おまけをテスト実行.
        """

        def get_prize_names(model_mgr, prizeid_list, using=backup_db):
            prizelist = BackendApi.get_prizelist(model_mgr, prizeid_list, using=using)
            prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=using)
            prize_names = []

            for prizeitem in prizeinfo['listitem_list']:
                prize_names.append(prizeitem['smalltext'])

            return prize_names

        model_mgr = self.getModelMgr()
        omakedict = {}

        for bonus in gachamaster.bonus:
            prize_id = bonus["prize"][0]
            prize_names = get_prize_names(model_mgr, [prize_id])

            omakedict[prize_id] = {}
            omakedict[prize_id]['prize_names'] = ' / '.join(prize_names)
            omakedict[prize_id]['bonus_rate_s'] = float(bonus["rate"]) / sum(item['rate'] for item in gachamaster.bonus) * 100
            omakedict[prize_id]['occurrences'] = 0
            omakedict[prize_id]['rate'] = 0

        for _ in xrange(cnt):
            prize_id = gachamaster.choice_bonus()[0]
            omakedict[prize_id]['occurrences'] += 1
            omakedict[prize_id]['rate'] = float(omakedict[prize_id]['occurrences']) / cnt * 100

        omakedict = OrderedDict(sorted(omakedict.items(), key=lambda x: x[1]['occurrences'], reverse=True))
        self.html_param['omakedict'] = omakedict


def main(request):
    return Handler.run(request)
