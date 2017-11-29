# coding: utf-8
from django.core.management.base import BaseCommand
import settings
from platinumegg.app.cabaret.models.UserLog import UserLogGacha
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Gacha import GachaMaster
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from collections import defaultdict


class Command(BaseCommand):
    """
        Script to send appropriate prizes to users
        who didn't receive any prize after playing the gacha 5STEP目, 6STEP目 and 7STEP目
        This error occured between 2017-02-09 16:00:00 and 2017-02-10 14:00:00
    """

    def handle(self, *args, **options):
        print 'Start check userloggacha userdata...'

        loguserdata = self._get_loguserdata()
        print "Finished checking succesfully. OK!! \n"

        print "Sending prizes....."

        textid = 255 # STEPUPガチャの補填
        def tr(data, prize):
            model_mgr = ModelRequestMgr()
            for uid, count in data.items():
                prizeidlist = [prize] * count
                prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=settings.DB_READONLY)
                print "%d: prizes=> %d  (%d time(s))" % (uid, prize, count)
                BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)
            model_mgr.write_all()
            return model_mgr

        for data in loguserdata.items():
            prize = data[0]
            try:
                db_util.run_in_transaction(tr, data[1], prize).write_end()
            except CabaretError as err:
                print('Error...{}'.format(err))

        print "Finshing sending prizes."
        print "Done."

    def _get_loguserdata(self):
        model_mgr = ModelRequestMgr()

        gachamasteridlist = [557, 558, 559] # ステップガチャ 5,6,7
        gachamasters = model_mgr.get_models(GachaMaster, gachamasteridlist, using=settings.DB_READONLY)
        continuitydict = {master.id:master.continuity for master in gachamasters}
        loguserdata = {}

        # the error occured between 2017-02-09 16:00:00 and 2017-02-10 14:00:00
        # therefore we filter the User Log using this parameters
        filters = dict(ctime__gte=DateTimeUtil.strToDateTime('2017-02-09 16:00:00', '%Y-%m-%d %H:%M:%S'),
                       ctime__lte=DateTimeUtil.strToDateTime('2017-02-10 14:00:00', '%Y-%m-%d %H:%M:%S'))

        tmpdict = {continuity:defaultdict(int) for continuity in continuitydict.values()}

        for model in UserLogGacha.fetchValues(filters=filters):
            uid, ctime, logdata = model.uid, model.ctime, model.data
            continuity = logdata.get('continuity')
            if continuity in continuitydict.values():
                tmpdict[continuity][uid] += 1

        """
            ID's form PrizeMaster
            611045 => 5STEP目は「琥珀のかんざし」
            611044 => 6STEP目は「花魁のかんざし」
            400401 => 7STEP目は「ティアラ」
        """
        loguserdata[611045] = tmpdict.pop(8)
        loguserdata[611044] = tmpdict.pop(11)
        loguserdata[400401] = tmpdict.pop(19)

        return loguserdata
