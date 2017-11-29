# -*- coding: utf-8 -*-
import settings
import settings_sub
from copy import copy
from defines import Defines
from django.db.models import Max
from django.db.utils import DatabaseError
from django.db import models, transaction
from django.db.backends.util import truncate_name
from platinumegg.app.cabaret.models.base.fields import CantReadField,\
    TinyIntField, AppDateTimeField
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.base.queryset import PIQuerySet, Query
from platinumegg.app.cabaret.models.base import save_custom_retries
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.util import dict_to_choices


class BaseModel(models.Model):
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = True
    _style = None
    
    @property
    def current_db(self):
        return self._state.db or settings.DB_DEFAULT
    
    #------------------------------------------------------------
    # defines..
    @classmethod
    def class_name(cls):
        return cls.__name__
    @classmethod
    def get_tablename(cls):
        """実際のテーブル名は {{project_name}}_{{model_name}} を全て小文字にしたもの.
        """
        return cls._meta.db_table
    
    @classmethod
    def get_primarykey_column(cls):
        """プライマリキー設定されたカラム名.
        """
        return cls._meta.pk.attname
    
    @classmethod
    def get_primarykey_field(cls):
        """プライマリキー設定されたフィールド.
        """
        return cls._meta.pk
    
    @classmethod
    def get_column_names(cls):
        arr = getattr(cls, '_column_names', None)
        if arr is None:
            arr = [field.name for field in cls.get_fields()]
            setattr(cls, '_column_names', arr)
        return arr
    
    @classmethod
    def _get_updatable_column_names(cls):
        arr = getattr(cls, '_not_fixed_column_names', None)
        if arr is None:
            fixed_columns = list(getattr(cls, 'FIXED_COLUMNS', []))
            fixed_columns.append(cls.get_primarykey_column())
            arr = list(set(cls.get_column_names()) - set(fixed_columns))
            setattr(cls, '_not_fixed_column_names', arr)
        return arr
    
    def get_updatable_column_names(self):
        return self.__class__._get_updatable_column_names()
    
    @classmethod
    def get_fields(cls):
        return cls._meta.fields[:]
    
    @classmethod
    def get_field(cls, column_name):
        for field in cls._meta.fields:
            if column_name == field.attname:
                return field
        return None
    
    @classmethod
    def pkey_to_str(cls, pkey):
        return str(pkey)
    
    @classmethod
    def str_to_pkey(cls, st):
        return int(st)
    
    def get_column_items(self):
        dic = {}
        for field in self.__class__.get_fields():
            dic[field.name] = getattr(self, field.name)
        return dic
    
    def get_class_name(self):
        return self.__class__.__name__
    
    def key(self):
        """ プライマリキーの値を取得.
        """
        return self.__getattribute__(self.get_primarykey_column())
    
    @classmethod
    def has_column(cls, column_name):
        """対象のカラムを持ったテーブルか
        """
        for field in cls._meta.fields:
            if column_name == field.attname:
                return True
        return False
    
    @classmethod
    def makeAutoCreateIndexName(cls, column):
        """Syncdbで自動的に作られるインデクス名を偽造.
        """
        if BaseModel._style is None:
            from django.core.management.color import no_style
            BaseModel._style = no_style()
        
        from django.db import connections
        connection = connections[settings.DB_DEFAULT]
        qn = connection.ops.quote_name
        index_name = '%s_%s' % (cls.get_tablename(), ('%x' % (abs(hash((column,))) % 4294967296L)))
        return BaseModel._style.SQL_TABLE(qn(truncate_name(index_name, connection.ops.max_name_length())))
    
    #------------------------------------------------------------
    # query..
    @classmethod
    def all(cls, using='default'):
        return PIQuerySet(cls.objects.model, using=using)
    
    @classmethod
    def sql(cls, query, *args, **kwargs):
        """SQL直叩き...
        ﾀﾌﾟﾙしか返しません
        """
        query_values = []
        for v in args:
            if type(v) == list:
                query_values += v
            else:
                query_values.append(v)
        using = kwargs.get('using', settings.DB_DEFAULT)
        return Query(cls, query, query_values, using=using)
    
    #------------------------------------------------------------
    # get models..
    @classmethod
    def getByKey(cls, key, fields=None, filters=None, excludes=None, order_by=None, using=settings.DB_DEFAULT):
        """ユニークなidを指定してModelをGET.
        listで複数指定も可.
        """
        return cls.getValuesByKey(key, fields, filters, excludes, order_by, using)
    
    @classmethod
    def getByKeyForUpdate(cls, key):
        """ユニークなidを指定してfor updateでModelをGET.
        これはlistで複数指定できない.
        """
        objects = cls.all().filter(**{cls.get_primarykey_column():key}).for_update()
        try:
            return objects[0]
        except IndexError:
            return None
    
    @classmethod
    def fetchByKeyForUpdate(cls, keys):
        """ユニークなidを指定してfor updateでModelをGET.
        """
        objects = cls.all().filter(**{'%s__in' % cls.get_primarykey_column():keys}).for_update()
        return objects[:]
    
    @classmethod
    def getValuesByKey(cls, key, fields=None, filters=None, excludes=None, order_by=None, using=settings.DB_DEFAULT):
        return cls._getValuesByKey(key=key, fields=fields, filters=filters, excludes=excludes, order_by=order_by, using=using)
    
    @classmethod
    def _getValuesByKey(cls, key, fields=None, filters=None, excludes=None, order_by=None, using=settings.DB_DEFAULT):
        """ユニークなidを指定して、モデルをGET.
        fieldsを指定した場合、未指定のフィールドには CantReadField が代入されたモデルが返されます.
        listで複数指定も可.
        key: ユニークなid
        fields: 欲しいフィールド. None にすると、全フィールド取得.
        """
        if filters is None:
            filters = {}
        
        if type(key) == list:
            if len(key) == 1:
                filters[cls.get_primarykey_column()] = key[0]
                model = cls.getValues(fields, filters, excludes=excludes, order_by=order_by, using=using)
                if model:
                    return [model]
                else:
                    return []
            else:
                filters[cls.get_primarykey_column() + '__in'] = key
                return cls.fetchValues(fields, filters, excludes=excludes, order_by=order_by, limit=len(key), offset=0, using=using)
        else:
            filters[cls.get_primarykey_column()] = key
            return cls.getValues(fields, filters, excludes=excludes, order_by=order_by, using=using)
    
    @classmethod
    def getValues(cls, fields=None, filters=None, excludes=None, order_by=None, offset=0, using=settings.DB_DEFAULT):
        """DBのデータを1つだけ引っ張ってくる.
        """
        models = cls.fetchValues(fields, filters, excludes, order_by, 1, offset, using=using)
        if 0 < len(models):
            return models[0]
        else:
            return None
        
    @classmethod
    def __makeAllCantReadModel(cls):
        model = cls()
        for f in cls._meta.fields:
            # 有効なフィールドを代入.見つからなかったら読んではいけないフィールドに.
            model.__setattr__(f.attname, CantReadField)
        return model
        
    @classmethod
    def __newFromDict(cls, fields, d, all_cant_read_model):
        """ dict型からモデルのインスタンス生成.
        """
        model = copy(all_cant_read_model)
        
        for f in fields:
            # 有効なフィールドを代入.見つからなかったら読んではいけないフィールドに.
            value = d.get(f, CantReadField)
            model.__setattr__(f, value)
        
        model.__setattr__('_fields', fields) # dict から作成したことを示す.
        model._state.adding = False # DBにあったはずなので.
        
        return model
        
    @classmethod
    def fetchValues(cls, fields=None, filters=None, excludes=None, order_by=None, limit=-1, offset=0, fetch_deleted=False, using=settings.DB_DEFAULT):
        """DBのデータを引っ張ってくる.
            fields を指定した場合、未指定のフィールドには CantReadField が代入された、
            モデルクラスのインスタンスが生成される.
            
            fileter に指定する変数名の末尾につける評価文字と記号の対応..
                無し    =
                __gt    >
                __gte   >=
                __lt    <
                __lte   <=
        """
        query = cls.all(using)
        
        # 非公開フラグカラムのあるものは、公開中のもののみ取ってくるように.
        # このフラグはマスターデータにしかないのでなんとかなるはず.
        if not fetch_deleted and cls.has_column(Defines.PUBLISH_STATUS_COLUMN):
            if filters is None:
                filters = {}
            filters['%s__in' % Defines.PUBLISH_STATUS_COLUMN] = Defines.PublishStatus.OPEN_STATAS_LIST
        
        if filters is not None:
            query = query.filter(**filters)
        if excludes is not None:
            query = query.exclude(**excludes)
        if fields is not None:
            query = query.values(*fields)
        if order_by is not None:
            query = query.order_by(order_by)
        if limit == -1:
            models = query.fetch_all(offset)
        else:
            models = query.fetch(limit, offset)
        if fields is None:
            return list(models)
        # dict型の場合はいったんモデルクラスのインスタンスに変換.
        all_cant_read_model = cls.__makeAllCantReadModel()
        return [cls.__newFromDict(fields, d, all_cant_read_model) for d in models]
    
    @classmethod
    def getInstanceByKey(cls, key, fields=None, filters=None, using=settings.DB_DEFAULT):
        """モデルが無かった場合にNoneではなくデフォルトの値が入ったインスタンス返す.
        """
        key_list = key
        if type(key_list) != list:
            key_list = [key]
        tmp = cls.getByKey(key_list, fields=fields, filters=filters, using=using)
        models = {}
        for model in tmp:
            models[model.key()] = model
        
        ret = []
        for primary_key in key_list:
            model = models.get(primary_key, None)
            if model is None:
                model = cls.makeInstance(primary_key)
            ret.append(model)
        
        if type(key) == list:
            return ret
        else:
            return ret[0]
    
    @classmethod
    def makeInstance(cls, key):
        model = cls()
        primary_key_column = cls.get_primarykey_column()
        setattr(model, primary_key_column, key)
        return model
        
    #------------------------------------------------------------
    # save models..
    def save(self, force_insert=False, force_update=False, using=settings.DB_DEFAULT):
        """saveをｵｰﾊﾞｰﾗｲﾄﾞ.
        djangoがﾘﾄﾗｲしないので.
        """
        try:
            if transaction.is_managed(using=using):
                # トランザクション中.
                super(BaseModel, self).save(force_insert, force_update, using)
            else:
                # トランザクション外.
                save_custom_retries(super(BaseModel, self).save, force_insert, force_update, using)
        except DatabaseError, er:
            if force_update and isinstance(er.args, (str, unicode)) and 0 <= er.args[0].find('Forced update did not affect any rows'):
                # Changed = 0
                pass
            else:
                raise
    
    def update(self, fields=None):
        """update専用.
        """
        if self.key() == CantReadField:
            raise CabaretError('primaly key is invalid.')
        using = settings.DB_DEFAULT
        
        if fields is None:
            # 全てupdate.
            self.save(force_insert=False, force_update=True, using=using)
        else:
            # 更新するデータ.
            update_data = {}
            try:
                # プライマリキー.
                name = self.get_primarykey_column()
                primary_filter = {
                    name:getattr(self, name)
                }
                for name in fields:
                    value = getattr(self, name)
                    update_data[name] = value
            except AttributeError:
                # そんなｶﾗﾑないよ!!.
                raise CabaretError('%s object doesnt have attribute name=%s' % (self.__class__.__name__, name))
            # 中でﾘﾄﾗｲする.
            self.__class__.all(using=using).filter(**primary_filter).update(**update_data)
        
    def insert(self):
        """Insert専用.
        重複した場合はSQLのログを見る限り普通のINSERT文なのでMySQL側でエラーをはくと思われる.
        """
        self.save(force_insert=True, force_update=False, using=settings.DB_DEFAULT)
        
    @classmethod
    def get_or_insert(cls, **kwargs):
        """getするけどなければ作成してmodelを返す.
        """
        result = cls.objects.get_or_create(**kwargs)  # (model, flag)のﾀﾌﾟﾙ.
        return result[0]
    
    def delete(self, using=None):
        super(BaseModel, self).delete(using=settings.DB_DEFAULT)
    
    def is_from_dict(self):
        """ dict から生成された不完全なモデルなら True
        """
        
        try:
            return self.__getattribute__('_fields') != None
        except:
            pass
        return False
    
    @classmethod
    def count(cls, filters=None, excludes=None, using=settings.DB_DEFAULT):
        """対象のﾚｺｰﾄﾞ数.
        """
        query = cls.all(using)
        if filters is not None:
            query = query.filter(**filters)
        if excludes is not None:
            query = query.exclude(**excludes)
        return query.count()
    
    @classmethod
    def max_value(cls, field, default_value=None, using=settings.DB_DEFAULT):
        """あるフィールドの最大値.
        """
        data = cls.objects.aggregate(max_value=Max(field))
        if data:
            ret = data.get('max_value', default_value)
            if ret is None:
                ret = 0
            return ret
        return default_value
    
    def get_write_end_methods(self):
        """書き込み（更新、削除）が終了した後に呼び出される関数。
        ModelUpdateMGRで呼んでる。
        ModelUpdateMGR通さなかった時は呼ばれないので注意。
        {
            method_key:(func, args[], kwgs{},),
        }
        上記のような値で返す。
        method_keyは同じ処理が何度も呼ばれるのを防ぐため。
        """
        return {}
        
    @classmethod
    def updateByKey(cls, key, **kwargs):
        """id指定で更新.
        """
        filters = {
            cls.get_primarykey_column():key,
        }
        cls.all().filter(**filters).update(**kwargs)
    
    @classmethod
    def get_cache_ttl(cls):
        """モデルのキャッシュ時間.
        """
        return 0
    
    @classmethod
    def get_formfields(cls):
        pkeyname = cls.get_primarykey_column()
        fields = [pkeyname]
        for field in cls.get_fields():
            if not field.name in fields:
                fields.append(field.name)
        return fields

class Singleton(BaseModel):
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = True
    
    SINGLE_ID = 1
    id = TinyIntField(primary_key=True, default=SINGLE_ID)          #ID
    
    @classmethod
    def getSingletonModel(cls):
        model = cls.getByKey(Singleton.SINGLE_ID)
        return model

class BaseMaster(BaseModel):
    class Meta:
        abstract = True
    pubstatus = models.PositiveSmallIntegerField(default=Defines.PublishStatus.PUBLIC, choices=dict_to_choices(Defines.PublishStatus.NAMES), verbose_name="公開ステータス")
    edittime = AppDateTimeField(default=OSAUtil.get_datetime_min(), db_index=True, verbose_name=u'更新時間')
    
    @property
    def is_public(self):
        return self.pubstatus == Defines.PublishStatus.PUBLIC
    
    @classmethod
    def get_formfields(cls):
        pkeyname = cls.get_primarykey_column()
        fields = [pkeyname, 'pubstatus']
        for field in cls.get_fields():
            if not field.name in fields:
                fields.append(field.name)
        return fields
    
    @classmethod
    def makeID(cls, uid, mid):
        return (uid << 32) + mid

class BaseMasterWithName(BaseMaster):
    class Meta:
        abstract = True
    name = models.CharField(max_length=48, verbose_name=u'名前')
    text = models.TextField(verbose_name=u'テキスト', blank=True)
    
    @classmethod
    def get_formfields(cls):
        pkeyname = cls.get_primarykey_column()
        fields = [pkeyname, 'pubstatus', 'name', 'text']
        for field in cls.get_fields():
            if not field.name in fields:
                fields.append(field.name)
        return fields

class BaseMasterWithThumbnail(BaseMasterWithName):
    class Meta:
        abstract = True
    thumb = models.CharField(max_length=128, verbose_name=u'サムネイル', blank=True)
    
    @classmethod
    def get_formfields(cls):
        pkeyname = cls.get_primarykey_column()
        fields = [pkeyname, 'pubstatus', 'name', 'text', 'thumb']
        for field in cls.get_fields():
            if not field.name in fields:
                fields.append(field.name)
        return fields
