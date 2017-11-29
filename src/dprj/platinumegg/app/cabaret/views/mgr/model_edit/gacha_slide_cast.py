# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.Gacha import GachaSlideCastMaster,\
    GachaMaster
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = GachaSlideCastMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        id = AppModelChoiceField(GachaMaster, required=False, label=u'ガチャID')

    def setting_property(self):
        self.MODEL_LABEL = u'ガチャページのスライド設定'
        self.valid_error_num = 0

    def __valid_master(self, master):
        if not master.is_public:
            return

        if GachaMaster.getByKey(master.id) is None:
            raise ModelEditValidError(u'ガチャが存在しません.master=%d' % master.id)

        model_mgr = self.getModelMgr()
        if not isinstance(master.castlist, list):
            raise ModelEditValidError(u'castlistのJSONが壊れています.master=%d' % master.id)

        if self.valid_error_num < 10:
            for record in self.allmasters:
                if master.id == record.id:
                    self.valid_error_num += 1
                    raise ModelEditValidError(u'IDが重複しています.id={}'.format(master.id))

        # 旧式のデータを新方式に置き換える.
        castlist = []
        for v in master.castlist:
            if isinstance(v, (int, long)):
                castlist.append([v, ''])
                continue
            elif not isinstance(v, (list, tuple)) or len(v) != 2 or not isinstance(v[0], (int, long)) or not isinstance(v[1], (str,unicode,list)):
                raise ModelEditValidError(u'castlistは[[マスターID,画像]...]で設定してください.master=%d' % master.id)
            castlist.append(v)

        master.castlist = castlist
        castdict = dict(castlist)
        if len(BackendApi.get_cardmasters(castdict.keys(), arg_model_mgr=model_mgr).values()) != len(master.castlist):
            raise ModelEditValidError(u'castlistに重複または存在しないものが含まれています.master=%d' % master.id)

    def valid_insert(self, master):
        self.__valid_master(master)

    def valid_update(self, master):
        self.__valid_master(master)

    def allow_csv(self):
        return True

def main(request):
    return Handler.run(request)
