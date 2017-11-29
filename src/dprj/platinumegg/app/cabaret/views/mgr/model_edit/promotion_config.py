# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField
from platinumegg.app.cabaret.models.promotion.koihime import PromotionConfigKoihime
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.promotion import PromotionSettings
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from platinumegg.app.cabaret.models.promotion.csc import PromotionConfigCsc


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class FormBase(AppModelForm):
        
        schedule = AppModelChoiceField(ScheduleMaster, required=False, label=u'開催期間')
        
        def _valid_primary_key(self):
            return PromotionConfigKoihime.SINGLE_ID
    
    class FormKoihime(FormBase):
        class Meta:
            model = PromotionConfigKoihime
            exclude = (
                'id',
            )
    
    class FormCsc(FormBase):
        class Meta:
            model = PromotionConfigCsc
            exclude = (
                'id',
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
        self.MODEL_LABEL = u'クロスプロモーション設定'
    
    def getModelAll(self):
        """モデルを全取得.
        """
        model_mgr = self.getModelMgr()
        return [model_mgr.get_model(self.model_cls, self.model_cls.SINGLE_ID, get_instance=True, fetch_deleted=True)]
    
    def __valid_master(self, master):
        master.id = self.model_cls.SINGLE_ID
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)

