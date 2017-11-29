# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm
from defines import Defines
from platinumegg.app.cabaret.models.promotion.koihime import PromotionRequirementMasterKoihime
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.promotion import PromotionSettings
from platinumegg.app.cabaret.models.promotion.csc import PromotionRequirementMasterCsc


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class FormKoihime(AppModelForm):
        class Meta:
            model = PromotionRequirementMasterKoihime
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    class FormCsc(AppModelForm):
        class Meta:
            model = PromotionRequirementMasterCsc
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def getFormClass(self):
        self.__appname = self.request.get('appname', PromotionSettings.Apps.KOIHIME)
        self.html_param['promotion_appname'] = self.__appname
        self.html_param['promotion_apps'] = PromotionSettings.CONFIG.keys()
        return getattr(Handler, 'Form%s' % self.__appname)
    
    def makeModelEditLinkUrl(self, *args):
        url = UrlMaker.model_edit(self.content_name, *args)
        url = OSAUtil.addQuery(url, 'appname', self.__appname)
        return self.makeAppLinkUrlAdmin(url)
    
    def get_index_template_name(self):
        return 'model_edit/promotion_edit'
    
    def setting_property(self):
        self.MODEL_LABEL = u'クロスプロモーション条件'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)

