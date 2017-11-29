# -*- coding: utf-8 -*-
import StringIO
import cgi
import csv
import datetime
import os
import settings
import settings_sub
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models.fields import IntegerField, BooleanField, DateTimeField
from django.forms.fields import ChoiceField, Field
from django.forms.models import ModelForm, ModelChoiceField, \
    modelformset_factory, ModelChoiceIterator, model_to_dict
from django.forms.widgets import Select
from django.utils.encoding import force_unicode
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.forms import UploadFileForm
from defines import Defines
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.strutil import StrUtil
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util import db_util, rediscache
from platinumegg.app.cabaret.util.master_data import MasterData
from platinumegg.app.cabaret.models.base.fields import AppFormDateTimeField
from django.db import connections
from platinumegg.app.cabaret.models.base.models import Singleton
import codecs
from platinumegg.lib.pljson import Json
import io
import urllib2
import urlparse
from platinumegg.app.cabaret.util.api import BackendApi
from django import forms
from platinumegg.app.cabaret.models.View import CardMasterView



class AdminModelEditHandler(AdminHandler):
    """モデルの操作.
    """
    def setting_property(self):
        raise NotImplementedError
    
    def getModelAll(self):
        """モデルを全取得.
        """
        model_mgr = self.getModelMgr()
        return model_mgr.get_mastermodel_all(self.model_cls, fetch_deleted=True)
    
    def get_formfields(self):
        return self.model_cls.get_formfields() + self.model_form_cls.get_extra_fields()
    
    def getAdditionalProcess(self):
        """追加したいプロセス.
        return {
            'hoge' : function_hoge,
        }
        """
        return None

    def allow_csv(self):
        """CSV の確認用フォームの表示設定. オーバーライドして使う.
        """
        return False

    def process(self):
        
        self.model_form_cls = self.getFormClass()
        self.MASTER_EDITTIME_COLUMN = Defines.MASTER_EDITTIME_COLUMN
        self.setting_property() # 必要な値を定義.
        self.__new_version = True # by default, the management page is the new version
        
        self.model_cls = self.model_form_cls.Meta.model
        self.content_name = self.getUrlArgs('/model_edit/').get(0)
        
        fields = self.get_formfields()
        excludes = getattr(self.model_form_cls.Meta, 'exclude', [])
        self.model_form_cls.base_fields.keyOrder = [field for field in fields if not field in excludes]
        
        urlargs = self.getUrlArgs('/model_edit/%s/' % self.content_name)
        self.__ope = urlargs.get(0, 'list')
        if self.__ope == 'csv':
            self.__page = 0
        else:
            self.__page = int(urlargs.get(1, 1))

        version = urllib2.unquote(self.request.get("version") or "")
        if version == "old":
            self.__new_version = False
        
        self.html_param['url_model_edit_list'] = self.makeModelEditLinkUrl('list', self.__page)
        self.html_param['url_cancel'] = self.makeModelEditLinkUrl()
        url_csv = self.makeModelEditLinkUrl('csv', self.__get_csv_name())
        if url_csv[-1] == '/':
            url_csv = url_csv[:-1]
        self.html_param['url_csv'] = url_csv
        self.html_param['url_load_csv'] = self.makeModelEditLinkUrl('load_csv')
        self.html_param['MODEL_LABEL'] = self.MODEL_LABEL
        self.html_param['CHECK_CSV_FORM'] = self.allow_csv()
        self.allmasters = []
        if self.request.method == 'POST' and self.request.django_request.POST.get('csv_check') != 'on':
            self.allmasters = self.getModelAll()
        
        # ローカルだとうまくアップできないので代わりに見に行く場所指定.
        self.__local_datafileurl = os.path.join(settings_sub.TMP_DOC_ROOT, self.__get_csv_name())
        self.html_param['local_datafileurl'] = self.__local_datafileurl
        self.html_param['uploadform'] = UploadFileForm()
        is_singleton = isinstance(self.model_cls(), Singleton)
        self.html_param['is_singleton'] = is_singleton
        
        
        # 最終更新時間.
        last_update = None
        modellist = self.getModelAll()
        
        if self.MASTER_EDITTIME_COLUMN:
            for aa in modellist:
                edit_time = getattr(aa, self.MASTER_EDITTIME_COLUMN, None)
                if last_update is None:
                    last_update = edit_time
                elif last_update < edit_time:
                    last_update = edit_time
        if last_update is None:
            self.html_param['last_update'] = '更新なし'
        else:
            self.html_param['last_update'] = DateTimeUtil.dateTimeToStr(last_update)
        
        table = {
            'list':self.__proc_index,
            'csv':self.__proc_csv,
            'load_csv':self.__proc_load_csv,
        }
        table.update(self.getAdditionalProcess() or {})
        f = table.get(self.__ope, None)
        if f:
            f()
        else:
            self.response.set_status(404)
    
    def getFormClass(self):
        return self.__class__.Form
    
    def addFilterQuery(self, url):
        filters = self.request.get("filters")
        version = self.request.get("version")
        if filters:
            url = OSAUtil.addQuery(url, "filters", urllib2.quote(filters, ""))
        if version:
            url = OSAUtil.addQuery(url, "version", urllib2.quote(version, ""))
        return url
    
    def makeModelEditLinkUrl(self, *args):
        url = UrlMaker.model_edit(self.content_name, *args)
        return self.makeAppLinkUrlAdmin(self.addFilterQuery(url))
    
    def __get_csv_name(self):
        model_cls_name = self.model_cls.__name__
        lowers = model_cls_name.lower()
        arr = []
        for i in xrange(len(lowers)):
            if model_cls_name[i] != lowers[i] and 0 < i:
                arr.append('_')
            arr.append(lowers[i])
        return '%s.csv' % (''.join(arr))
    
    def __proc_index(self):
        """一覧.
        """
        infos = []
        if Defines.PUBLISH_STATUS_COLUMN in self.model_form_cls.base_fields.keyOrder:
            # 削除フラグは最後固定.
            self.model_form_cls.base_fields.keyOrder.remove(Defines.PUBLISH_STATUS_COLUMN)
            self.model_form_cls.base_fields.keyOrder.append(Defines.PUBLISH_STATUS_COLUMN)
        
        # 見出し部分.
        self.__make_captions()
        
        ModelFormSet = self.__get_modelformset_cls()
        
        # POSTされてきた時はその値を表示、何も無い時はそのページのコンテンツを表示.
        # すごくややこしい...
        page_contentnum = 50
        total_count = 0
        queryset = None
        if self.request.method == 'POST':
            
            self.checkDevelopment()
            
            post_data = self.request.django_request.POST
            model_form_set = ModelFormSet(post_data)
            
            if model_form_set.is_valid():
                instances = model_form_set.save(commit=False)
                url = self.__write_instances(instances)
                if url:
                    self.redirect(url)
                    return
            else:
                self.putAlertToHtmlParam(u'登録に失敗しました.エラー内容を確認ご確認下さい.', AlertCode.ERROR)
        else:
            filters = {}
            str_filters = urllib2.unquote(self.request.get("filters") or "")
            if str_filters:
                filters = dict(urlparse.parse_qsl(str_filters))
                self.html_param['model_filters'] = filters

            #order_byを入れないとなぜかModelFormSetでエラーがでる。
            pkey_name = self.model_cls.get_primarykey_column()
            queryset = self.model_cls.objects.order_by(pkey_name).filter(**filters)
            total_count = queryset.count()
            queryset = queryset[(self.__page - 1) * page_contentnum : self.__page * page_contentnum]

            model_form_set = ModelFormSet(queryset=queryset)

        modelforms = model_form_set.forms
        for form in modelforms:
            form_dict = vars(form)
            # 0レコードの場合、form_dict['initial'] は空辞書
            is_secret = True if form_dict['initial'] and form_dict['initial']['pubstatus'] in Defines.PublishStatus.CLOSED_STATAS_LIST else False
            info = {
                'form':form,
                'tr_class': 'class="danger"' if is_secret else ''
            }
            infos.append(info)

        func_add_pagenumber = lambda url,p:self.addFilterQuery(UrlMaker.model_edit(self.content_name, self.__ope, p+1))

        self.putPagenation('', self.__page - 1, total_count, page_contentnum, func_add_pagenumber=func_add_pagenumber)
        self.html_param['is_editable'] = self.is_editable()
        
        self.html_param['valid_csv_name'] = self.__get_csv_name()
        
        url = UrlMaker.model_edit(self.content_name)

        self.html_param['url_self'] = self.makeAppLinkUrlAdmin(url)
        if self.__new_version:
            self.html_param['url_self_switch'] = OSAUtil.addQuery(self.makeAppLinkUrl(url), 'version', 'old')
            self.html_param['switch_text'] = "古いバージョンに切り替えます"
        else:
            self.html_param['url_self_switch'] = self.makeAppLinkUrlAdmin(url)
            self.html_param['switch_text'] = "新しいバージョンに切り替えます"

        self.html_param['new_version'] = self.__new_version

        self.writeHtml(infos, model_form_set)
    
    def __tr_write(self, instances):
        for instance in instances:
            instance.save()
        self.valid_write_end()
    
    def __make_captions(self):
        connection = connections[settings.DB_DEFAULT]
        columns = []
        dbfield_dict = {}
        for field in self.model_cls._meta.fields:
            dbfield_dict[field.column] = field
        for field in self.model_form_cls():
            db_type = None
            dbfield = dbfield_dict.get(field.name, None)
            if dbfield is not None:
                db_type = dbfield.db_type(connection)
            columns.append({
                'label':field.label,
                'name':field.name,
                'help_text':field.help_text,
                'db_type':db_type,
            })
        self.html_param['columns'] = columns
        return columns
    
    def __get_modelformset_cls(self):
        extra = 0
        modelnum = self.model_cls.count(using=settings.DB_READONLY)
        if modelnum == 0:
            extra = 1
        ModelFormSet = modelformset_factory(self.model_cls, self.model_form_cls, extra=extra)
        ModelFormSet.form = self.model_form_cls # ここで上書きしないとカラムの並び順が変わらない.
        return ModelFormSet
    
    def checkDevelopment(self):
        if not settings_sub.IS_DEV:
            raise CabaretError(u'本番環境では登録できません', CabaretError.Code.NOT_AUTH)
    
    def writeHtml(self, infos, model_form_set):
        self.html_param['infos'] = infos
        self.html_param['formset'] = model_form_set
        
        # 追加の行のテンプレート用に空のフォームを一つ作る.
        self.html_param['default_form'] = self.model_form_cls()
        
        self.writeAppHtml(self.get_index_template_name())
    
    #===========================================================================
    # 使用テンプレート.
    #===========================================================================
    def get_index_template_name(self):
        return 'model_edit/base_index'
#    def get_insert_template_name(self):
#        return 'model_edit/base_insert'
#    def get_update_template_name(self):
#        return 'model_edit/base_update'
        
    #===========================================================================
    # 入力値チェック.
    #===========================================================================
    def valid_insert(self, master):
        """登録OKかチェック.
        エラーの時はModelEditValidError.
        """
    
    def valid_update(self, master):
        """更新OKかチェック.
        エラーの時はModelEditValidError.
        """
    
    def valid_delete(self, master):
        """消してOKかチェック.
        エラーの時はModelEditValidError.
        """
        if settings_sub.IS_DEV:
            return
        if not master._state.adding:
            raise ModelEditValidError(u'本番環境では公開フラグの設定はできません.')
    
    def valid_write_end(self):
        """書き込み後チェック.
        エラーの時はModelEditValidError.
        """
    
    def get_model_view_name(self, model):
        """表示するモデル名.
        〇〇の登録が完了しましたとかで使う.
        """
        return '%s:%s' % (model.get_primarykey_column(), model.key())
    
    def __proc_csv(self):
        """スプレッドシートで使える形式でcsv吐き出し.
        """
        def makeRow(sequence):
            return ','.join(sequence)
            
        key_table = {}
        for column in self.model_cls.get_column_names():
            key_table[column.replace('_', '')] = column
        for column in self.model_form_cls.get_extra_fields():
            key_table[column.replace('_', '')] = column
        
        csv_row_list = []
        
        model_all = self.getModelAll()
        columns = AdminModelEditHandler.__make_sheet_columns(self.model_form_cls)
        csv_row_list.append(makeRow(['"%s"' % column for column in columns]))
        
        for model in model_all:
            data_list = []
            for column in columns:
                attrname = key_table[column]
                if hasattr(model, attrname):
                    v = getattr(model, attrname)
                elif hasattr(model, 'get_%s' % attrname):
                    v = getattr(model, 'get_%s' % attrname)()
                else:
                    v = 'Unknown'
                if type(v) in (list, tuple, dict):
                    t = Json.encode(v)
                else:
                    t = str(v)
                t = t.replace('"','""')#escape.
                data_list.append('"%s"' % t)
            csv_row_list.append(makeRow(data_list))
        
        # 書き込む.
        csv_data = ''
        for row in csv_row_list:
            csv_data += '%s\n' % row
        
        csv_data = StrUtil.to_s(csv_data, dest_enc='shift-jis')#Excelで開くと文字化けするのでshift-jisに.
        self.osa_util.write_csv_data(csv_data, self.__get_csv_name())
    
    def __proc_load_csv(self):
        if self.request.method == 'POST':
            fixture = None
            tmp_data = None
            if settings_sub.IS_LOCAL:
                # ローカルだとアップできないので..
                f = None
                try:
                    f = open(self.__local_datafileurl, 'r')
                    tmp_data = f.read()
                except IOError:
                    tmp_data = None
                finally:
                    if f:
                        f.close()
            else:
                request_files = self.request.files
                form = UploadFileForm(self.request.body, request_files)
                if form.is_valid():
                    req_file = request_files['data_file']
                    csv_name = self.__get_csv_name()
                    if req_file.name != csv_name:
                        url = self.makeModelEditLinkUrl()
                        url = self.setAlert(url, u'ファイル名が不正です.正しいファイル名は%sです.' % csv_name, AlertCode.ERROR)
                        self.redirect(url)
                        return
                    tmp_data = req_file.read()
            if tmp_data:
                src_enc = StrUtil.guess_charset(tmp_data)
                fixture = io.StringIO(StrUtil.to_u(tmp_data, src_enc), newline=None)
            
            sheet_columns = AdminModelEditHandler.__make_sheet_columns(self.model_form_cls)
            pkey_name = self.model_cls.get_primarykey_column()
            sheet_pkey_name = pkey_name.replace('_', '')
            
            model_all = self.model_cls.fetchValues(using=settings.DB_DEFAULT)
            model_dict = {}
            for model in model_all:
                model_dict[model.key()] = model
            
            save_models = []
            
            if fixture:
                cnt = 0
                indexes = {}
                for row in csv.reader(fixture):
                    if cnt == 0:
                        # ここはカラム名.
                        index = 0
                        for column_name in row:
                            indexes[column_name] = index
                            index += 1
                    else:
                        # ここは値.
                        pkey = row[indexes.get(sheet_pkey_name, 0)]
                        model = model_dict.get(pkey, self.model_cls(**{pkey_name:pkey}))
                        field_dict = dict([(field.attname, field) for field in self.model_cls.get_fields()])
                        for column in self.get_formfields():
                            sheet_column = column.replace('_', '')
                            if not sheet_column in sheet_columns:
                                continue
                            field = field_dict.get(column) or self.model_form_cls.declared_fields.get(column)
                            
                            index = indexes.get(sheet_column, None)
                            if index is not None:
                                str_v = row[index]
                                try:
                                    v = self.str_to_fieldvalue(field, str_v)
                                except Exception, e:
                                    raise CabaretError('[field=%s,value=%s,row=%s,data=%s]%s:%s' % (column, str_v, cnt, row, e.__class__.__name__, e))
                            else:
                                # modelにはあるが実際のシートに無い場合.
                                v = getattr(model, column, None)
                                if v is None:
                                    raise CabaretError(u'dataError:[field=%s,pkey=%s,data=%s]' % (column, pkey, row))
                            if hasattr(model, 'set_%s' % column):
                                getattr(model, 'set_%s' % column)(v)
                            else:
                                setattr(model, column, v)
                        save_models.append(model)
                    cnt += 1
            url = self.__write_instances(save_models)
            if not url:
                url = self.makeModelEditLinkUrl()
                url = self.setAlert(url, u'データがありません', AlertCode.ERROR)
            self.redirect(url)
        else:
            self.__proc_index()

    def __write_instances(self, instances):
        """インスタンス一覧を書き込み.
        """
#        instances = model_form_set.save(commit=False)
        url = None
        if 0 < len(instances):
            can_save = True
            url = self.makeModelEditLinkUrl(self.__ope, self.__page)
            add_instances = []
            edit_instances = []
            now = datetime.datetime.now()
            
            errors = []
            for instance in instances:
                
                if self.MASTER_EDITTIME_COLUMN:
                    setattr(instance, self.MASTER_EDITTIME_COLUMN, now) # 編集時間更新.
                
                try:
                    pub_status = getattr(instance, Defines.PUBLISH_STATUS_COLUMN, Defines.PublishStatus.PUBLIC)
                    if pub_status in [Defines.PublishStatus.SECRET, Defines.PublishStatus.PUBLIC_DEV]:
                        # 削除フラグが立てられた時のチェック.
                        self.valid_delete(instance)
                    
                    if instance._state.adding:
                        self.valid_insert(instance)
                        add_instances.append(instance)
                    else:
                        self.valid_update(instance)
                        edit_instances.append(instance)
                except ModelEditValidError, e:
                    errors.append(unicode(e))
                    can_save = False
            if errors:
                url = self.setAlert(url, '<br />'.join(errors), AlertCode.ERROR)
            
            if can_save:
                try:
                    db_util.run_in_transaction_custom_retries(0, self.__tr_write, instances)
                except ModelEditValidError, e:
                    url = self.setAlert(url, unicode(e), AlertCode.ERROR)
                else:
                    self.reload()
                    
                    txt_dic = {"txt":u''}
                    def __addTxt(v):
                        max_length = 1024
                        if max_length < len(txt_dic['txt']):
                            return
                        txt_dic['txt'] += '%s<br />' % v
                        if max_length < len(txt_dic['txt']):
                            txt_dic['txt'] += 'and more...'
                    
                    __addTxt(u'保存が完了しました。')
                    __addTxt(u'<strong>登録</strong>')
                    
                    for ins in add_instances:
                        __addTxt(self.get_model_view_name(ins))
                    if not add_instances:
                        __addTxt('　無し')
                    
                    
                    __addTxt(u'<strong>編集</strong>')
                    for ins in edit_instances:
                        __addTxt(self.get_model_view_name(ins))
                    if not edit_instances:
                        __addTxt('　無し')
                    
                    url = self.setAlert(url, txt_dic['txt'], AlertCode.SUCCESS)
        return url
    
    #=====================================================================
    # etc.
    def is_editable(self):
        """リリース環境で編集可能フラグ.
        """
        return True
#        return settings_sub.IS_DEV
    
    def reload(self):
        """マスターデータをリロード.
        """
        now_diff = OSAUtil.get_now_diff()
        MasterData.incrementEditCacheVersion()
        rediscache.flush_all()
        OSAUtil.get_cache_client().flush()
        if settings_sub.IS_DEV:
            OSAUtil.set_now_diff(now_diff)
    
    @staticmethod
    def str_to_fieldvalue(field, str_v):
        if str_v is None:
            return None
        
        if isinstance(field, (IntegerField, forms.IntegerField)):
            return int(str_v)
        elif isinstance(field, BooleanField):
            return str_v.lower() in ('1', 'true')
        elif isinstance(field, DateTimeField):
            a = AppFormDateTimeField()
            return a.to_python(str_v)
#            return datetime.datetime.strptime(str_v, '%Y-%m-%d %H:%M:%S+00:00')
        else:
#            src_enc = StrUtil.guess_charset(str_v)
#            str_v = StrUtil.to_s(str_v, dest_enc='utf-8', src_enc=src_enc)#mysqlの文字コードに合わせる.
            return str_v
    
    @staticmethod
    def __fieldname_to_csvcolumnname(fieldname):
        return fieldname.replace('_', '')
    
    @staticmethod
    def __make_sheet_columns(model_form_cls):
        columns = [AdminModelEditHandler.__fieldname_to_csvcolumnname(field.name) for field in model_form_cls()]
        if 'pubstatus' in columns:
            columns.remove('pubstatus')
            columns.append('pubstatus')
        if 'edittime' in columns:
            columns.remove('edittime')
        return columns
    
    def checkPrize(self, target_master, prizeidlist, name=None, column_name=None):
        if len(prizeidlist) != len(list(set(prizeidlist))):
            raise ModelEditValidError(u'%sが重複しています.%s=%d' % (name or u'報酬', column_name or target_master.get_primarykey_column(), target_master.key()))
        prizelist = BackendApi.get_prizemaster_list(self.getModelMgr(), prizeidlist)
        if len(prizeidlist) != len(prizelist):
            raise ModelEditValidError(u'%sに存在しない報酬が設定されています.%s=%d' % (name or u'報酬', column_name or target_master.get_primarykey_column(), target_master.key()))
    
class AppModelSelect(Select):
    def _has_changed(self, initial, data):
        """毎回0 != '' の変更書き込みしちゃうのでデフォで0にしてみる.
        """
        if data == '':
            data = 0
        return Select._has_changed(self, initial, data)

class AppModelChoiceField(ModelChoiceField):
    """
    普通のModelChoiceFieldだと勝手にオブジェクトに変換されたりするので.
    """
    def __init__(self, *args, **kwgs):
        ModelChoiceField.__init__(self, widget=AppModelSelect, *args, **kwgs)
    
    def label_from_instance(self, obj):
        if getattr(obj, 'name', None) is None:
            return '%sID:%s' % (obj.__class__.__name__, obj.id)
        return u'%s（id:%s）' % (obj.name, obj.id)
    def to_python(self, value):
        return value
    def clean(self, value):
        if value == '' and not self.required:
            value = 0 # 必須じゃない場合はempty valueが来たらID0を指定.
        return ModelChoiceField.clean(self, value)

class ScheduleChoiceField(AppModelChoiceField):
    """ScheduleのIDを設定するためのフィールド.
    """
    def label_from_instance(self, obj):
        return u'%s' % (obj.comment)
        
class AppModelForm(ModelForm):
    
    def __init__(self, *args, **kwgs):
        super(AppModelForm, self).__init__(*args, **kwgs)
        
        # プライマリーキーを共通でvalidateするために、clean_COLUMN_NAMEのメソッドを動的に定義する.
        method_name = 'clean_%s' % self.Meta.model.get_primarykey_column()
        self.__dict__[method_name] = self._valid_primary_key
        
        # 編集ページだけのフィールドの値をフォームに設定.
        for fieldname in self.__class__.get_extra_fields():
            if hasattr(self.instance, fieldname):
                v = getattr(self.instance, fieldname)
            else:
                gettername = 'get_{}'.format(fieldname)
                if hasattr(self.instance, gettername):
                    v = getattr(self.instance, gettername)()
                else:
                    continue
            self.initial[fieldname] = v
    
    def _valid_primary_key(self):
        p_key = self.Meta.model.get_primarykey_column()
        p_value = self.cleaned_data.get(p_key)
        if p_value <= 0:
            raise ValidationError(u'%sは1以上を指定して下さい' % p_key)
        return p_value
    
#    @classmethod
#    def change_key_order(cls, key_order):
#        # カラムの順番を入れ替えたい時はここで変更.
#        pass
    
    @classmethod
    def get_extra_fields(cls):
        if not hasattr(cls, '_extra_fields'):
            extra_fields = list(set(cls.declared_fields.keys()) - set(cls.Meta.model.get_column_names()))
            extra_fields.sort(key=lambda x:cls.declared_fields.keys().index(x))
            setattr(cls, '_extra_fields', extra_fields)
        return getattr(cls, '_extra_fields')
    
    def save(self, *args, **kwargs):
        # 編集ページだけのフィールドの値をモデルに設定.
        for fieldname in self.__class__.get_extra_fields():
            v = self.cleaned_data[fieldname]
            if hasattr(self.instance, fieldname):
                setattr(self.instance, fieldname, v)
            else:
                settername = 'set_{}'.format(fieldname)
                if hasattr(self.instance, settername):
                    getattr(self.instance, settername)(v)
        return super(AppModelForm, self).save(*args, **kwargs)

class ModelEditValidError(Exception):
    pass

#def main(request):
#    return AdminHandler.run(Handler, request)
