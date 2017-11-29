# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.models.promotion.koihime import PromotionPrizeMasterKoihime
from platinumegg.app.cabaret.util.promotion import PromotionSettings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.promotion.csc import PromotionPrizeMasterCsc


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class FormKoihime(AppModelForm):
        class Meta:
            model = PromotionPrizeMasterKoihime
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        schedule = AppModelChoiceField(ScheduleMaster, required=False, label=u'開催期間')
        prize_text = AppModelChoiceField(TextMaster, required=False, label=u'報酬テキスト')
    
    class FormCsc(AppModelForm):
        class Meta:
            model = PromotionPrizeMasterCsc
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        schedule = AppModelChoiceField(ScheduleMaster, required=False, label=u'開催期間')
        prize_text = AppModelChoiceField(TextMaster, required=False, label=u'報酬テキスト')
    
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
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        model_mgr = self.getModelMgr()
        
        prizes = master.prizes
        if len(prizes) != len(list(set(prizes))):
            raise ModelEditValidError(u'報酬が重複しています.master=%d' % master.id)
        
        prizelist = BackendApi.get_prizemaster_list(model_mgr, prizes)
        if len(prizes) != len(prizelist):
            raise ModelEditValidError(u'存在しない報酬が設定されています.master=%d' % master.id)
    
    def setting_property(self):
        self.MODEL_LABEL = u'クロスプロモーション報酬'
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)

