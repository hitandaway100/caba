# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.models.View import CardMasterView
from platinumegg.app.cabaret.models.Skill import SkillMaster
from platinumegg.app.cabaret.models.CardLevelExp import CardLevelExpMster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = CardMasterView
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
                'albumhklevel',
            )
        skill = AppModelChoiceField(SkillMaster, required=False, label=u'サービス(スキル)')
    
    def setting_property(self):
        self.MODEL_LABEL = u'カード'
        self.valid_error_num = 0
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        if not master.gtype in Defines.CardGrowthType.NAMES.keys():
            raise ModelEditValidError(u'成長タイプが不正です.card=%d' % master.id)
        elif 1 < master.hklevel and not master.rare in Defines.Rarity.EVOLUTION_ABLES:
            raise ModelEditValidError(u'レア度とハメ管理度の組み合わせが不正です.card=%d' % master.id)
        elif not (1 <= master.hklevel <= Defines.HKLEVEL_MAX):
            raise ModelEditValidError(u'ハメ管理度が不正です.card=%d' % master.id)
        elif 0 < master.skill and self.getModelMgr().get_model(SkillMaster, master.skill) is None:
            raise ModelEditValidError(u'存在しないスキルが設定されています.card=%d' % master.id)

        if self.valid_error_num < 10:
            for record in self.allmasters:
                if master.id == record.id:
                    self.valid_error_num += 1
                    raise ModelEditValidError(u'キャストIDが重複しています.id={}'.format(master.id))

    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)
    
    def valid_write_end(self):
        master_all = {}
        albumset = {}
        for master in CardMasterView.fetchValues():
            master_all[master.id] = master
            arr = albumset[master.album] = albumset.get(master.album, [])
            arr.append(master)
        
        maxlevel = CardLevelExpMster.max_value('level') or 0
        
        errors = []
        for master in master_all.values():
            album_arr = albumset.get(master.album, [])
            if master.ckind == Defines.CardKind.NORMAL and master.rare in Defines.Rarity.EVOLUTION_ABLES:
                length = Defines.HKLEVEL_MAX
            else:
                length = 1
            if len(album_arr) != length:
                errors.append(u'同じアルバムのカード数が不正です, card=%d,album=%d' % (master.id, master.album))
            if maxlevel < master.maxlevel:
                errors.append(u'カードの経験値テーブルにない最大レベルです, card=%d' % master.id)
        if errors:
            raise ModelEditValidError('<br />'.join(errors))

    def allow_csv(self):
        return True

def main(request):
    return Handler.run(request)
