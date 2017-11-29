# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.api import db_util
from platinumegg.app.cabaret.models.NgCast import NgCastMaster
from platinumegg.app.cabaret.models.View import CardMasterView
from platinumegg.app.cabaret.util.alert import AlertCode
from defines import Defines
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from collections import defaultdict


class Handler(AdminHandler):
    """NGキャスト管理.
    """

    def process(self):
        model_mgr = self.getModelMgr()
        args = self.getUrlArgs('/ng_cast/')
        ope = args.get(0)
        func = getattr(self, '_proc_%s' % ope, None)
        if func:
            func()

        ngcastmasters = NgCastMaster.fetchValues(using=settings.DB_READONLY)
        ngcastmasters_dict = {ngcast.id: ngcast.flag for ngcast in ngcastmasters}
        cardmasters = BackendApi.get_model_list(model_mgr, CardMasterView, [x.id for x in ngcastmasters], using=settings.DB_READONLY)        

        ngcasts_each_album = defaultdict(list)
        for cardmaster in cardmasters:
            flag = ngcastmasters_dict[cardmaster.id]
            ngcasts_each_album[cardmaster.album].append({"name":cardmaster.name,"id":cardmaster.id, "flag": flag})

        self.html_param['ngcasts_each_album'] = ngcasts_each_album
        self.html_param['url_add'] = self.makeAppLinkUrlAdmin(UrlMaker.ng_cast('add'))
        self.html_param['url_edit'] = self.makeAppLinkUrlAdmin(UrlMaker.ng_cast('edit'))
        self.writeAppHtml('ng_cast')

    def _proc_add(self):
        """NGキャストを追加.
        """
        model_mgr = self.getModelMgr()
        name = self.request.get('_name', '').strip()
        is_checked = self.request.get('ngcast_check')

        # Does the a card with the name "cast_name" exists in CardMaster?
        cardmaster = CardMasterView.fetchValues(filters={'name': name})
        if not cardmaster:
            self.putAlertToHtmlParam(u'保存されていないキャストです', AlertCode.ERROR)
            return False

        model_values = {card.id:card.name for card in cardmaster}

        def tr_write(model_values):
            def forUpdate(model, inserted, name):
                model.name = name

            for cast_id, cast_name in model_values.items():
                model_mgr.add_forupdate_task(NgCastMaster, cast_id, forUpdate, cast_name)
            model_mgr.write_all()
            return model_mgr

        try:
            tmp_model_mgr = db_util.run_in_transaction(tr_write, model_values)
        except CabaretError, err:
            print "A Cabaret error occured: %s" % err.value
            return

        tmp_model_mgr.write_end()

        self.putAlertToHtmlParam(u'%sをNGキャストに登録しました' % name, AlertCode.SUCCESS)

    def _proc_edit(self):
        """NGCキャストのflagを変更する
        """
        is_checked = self.request.get('ngcast_check')
        ngcasts = NgCastMaster.fetchValues()

        def tr_update():
            model_mgr = self.getModelMgr()
            for cast in ngcasts:
                cast.flag = True if is_checked else False
                model_mgr.set_save(cast)
            model_mgr.write_all()
            return model_mgr

        try:
            tmp_model_mgr = db_util.run_in_transaction(tr_update)
        except CabaretError, err:
            print "A Cabaret error occured: %s" % err.value
            return

        tmp_model_mgr.write_end()

    """
    def _proc_rem(self):
        # NGキャストから削除

        model_mgr = self.getModelMgr()
        name = self.request.get('_name')

        modellist = [model for model in NgCastMaster.fetchValues(filters={'name': name})]
        if not modellist:
            self.putAlertToHtmlParam(u'指定したユーザ名が不正です', AlertCode.ERROR)
            return

        def tr_delete(modellist):
            for model in modellist:
                model_mgr.set_delete(model)
            model_mgr.write_all()
            return model_mgr

        try:
            tmp_model_mgr = db_util.run_in_transaction(tr_delete, modellist)
        except CabaretError, err:
            print "A Cabaret error occured: %s" % err.value
            return

        tmp_model_mgr.write_end()

        self.putAlertToHtmlParam(u'%sをNGキャストから削除されました' % name, AlertCode.SUCCESS)
    """


def main(request):
    return Handler.run(request)
