# -*- coding: utf-8 -*-
import cPickle
import datetime
import re
from django import forms
from django.core import exceptions
from django.db import models
from platinumegg.lib.pljson import Json
from platinumegg.lib import timezone
from platinumegg.lib.strutil import StrUtil


class CantReadField:
    """ 読んではいけないフィールドを示すクラス.
    """
    pass

class TinyIntField(models.IntegerField):
    """tinyintﾌｨｰﾙﾄﾞ
    """
    empty_strings_allowed = False
    def get_internal_type(self):
        return "TinyIntField"
    def db_type(self, *args, **kwargs):
        return "TINYINT"

class PositiveAutoField(models.AutoField):
    """unsigned属性を付けたintegerのauto_incrementﾌｨｰﾙﾄﾞ
    """
    empty_strings_allowed = False
    def get_internal_type(self):
        return "PositiveAutoField"
    def db_type(self, *args, **kwargs):
        return "INTEGER UNSIGNED AUTO_INCREMENT"

class PositiveBigAutoField(models.AutoField):
    """unsigned属性を付けたbigintegerのauto_incrementﾌｨｰﾙﾄﾞ
    """
    empty_strings_allowed = False
    
    def get_internal_type(self):
        return "PositiveBigAutoField"
    def db_type(self, *args, **kwargs):
        return "bigint UNSIGNED AUTO_INCREMENT"

class PositiveBigIntegerField(models.PositiveIntegerField):
    """Represents MySQL's unsigned BIGINT data type (works with MySQL only!)
    """
    empty_strings_allowed = False
    
    def get_internal_type(self):
        return "PositiveBigIntegerField"
    
    def db_type(self, *args, **kwargs):
        # This is how MySQL defines 64 bit unsigned integer data types
        return "bigint UNSIGNED"

class BlobField(models.Field):
    """Blob型が使いたい。
    """
    __metaclass__ = models.SubfieldBase
    
    def db_type(self, connection):
        # mysql only...
        return 'BLOB'

class TextAreaCharField(models.CharField):
    """char型だけどフォームでテキストエリアを表示.
    """
    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(TextAreaCharField, self).formfield(**defaults)

class JsonInput(forms.Textarea):
    def render(self, name, value, attrs=None):
        try:
            value = Json.encode(value, ensure_ascii=False)
        except:
            pass
        return super(JsonInput, self).render(name, value, attrs=attrs)

class JsonCharField(models.TextField):
    """char型で中身はjsonな形式であってほしいフィールド.
    """
    default_error_messages = {'notjson':u'JSON形式で入力して下さい'}
    
    def __init__(self, *args, **kwargs):
        kwargs['blank'] = kwargs.get('blank', True)
        models.TextField.__init__(self, *args, **kwargs)
    
    def validate(self, value, model_instance):
        # json.loadsができるかどうか確認.
        if not self.editable:
            # Skip validation for non-editable fields.
            return
        
        models.TextField.validate(self, value, model_instance)
        try:
            Json.encode(value, ensure_ascii=False)
        except:
            raise exceptions.ValidationError(self.error_messages['notjson'])
    
    __metaclass__ = models.SubfieldBase
    def to_python(self, value):
        """
        loadsしてみて成功したら結果を返す。
        失敗したらそのまま返す。
        """
        if isinstance(value, unicode):
            value = StrUtil.to_s(value)
        if isinstance(value, str):
            try:
                value = Json.decode(value)
            except:
                pass
        return value
    
    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        return Json.encode(value, ensure_ascii=False)
    
    def formfield(self, **kwargs):
        defaults = {'widget': JsonInput}
        defaults.update(kwargs)
        return super(JsonCharField, self).formfield(**defaults)

class AppDateTimeField(models.DateTimeField):
    """アプリで使うTZ <-> 鯖で使うTZ
        を良い感じに入れ替えて使う.
    """
    
    def __init__(self, *args, **kwgs):
        models.DateTimeField.__init__(self, *args, **kwgs)
        
    __metaclass__ = models.SubfieldBase
    def to_python(self, value):
        """ DB -> Python.
        """
        if value == CantReadField:
            return value
        value = super(AppDateTimeField, self).to_python(value)
        if value is None:
            return self.get_default() or None
        value = value.replace(tzinfo=timezone.TZ_DB)  #DBのtzをセット.
        value = value.astimezone(timezone.TZ_DEFAULT) # TZ_DEFAULTにする.
        return value
        
    def get_db_prep_value(self, value, connection, prepared=False):
        """ Python -> DB.
        """
        value = value.astimezone(timezone.TZ_DB) # TZ_DEFAULTからTZ_DBにする.
        # 保存する時にtzinfoが残っているとエラー吐くので削除.
        value = value.replace(tzinfo=None)
        prepared = True
        return models.DateTimeField.get_db_prep_value(self, value, connection=connection, prepared=prepared)
    
    def formfield(self, **kwargs):
        defaults = {'form_class': AppFormDateTimeField}
        defaults.update(kwargs)
        return super(AppDateTimeField, self).formfield(**defaults)

class AppFormDateTimeField(forms.DateTimeField):
    """フォームのフィールド.
    フォームの入力値を受け取る。
    文字列にTZ情報が書かれていたらそのタイムゾーンを適用.（+0900のような表記）
    指定が無ければTZ_DEFAULTで受け取る.（TZ_DEFAULTで出力してるの）
    """
    # 2009-06-04 12:00:00+01:00 or 2009-06-04 12:00:00 +0100
    TZ_OFFSET = re.compile(r'^(.*?)\s?([-\+])(\d\d):?(\d\d)$')
    
    def to_python(self, value):
        """Form -> Python.
        """
        try:
            value = super(AppFormDateTimeField, self).to_python(value)
        except exceptions.ValidationError:
            match = AppFormDateTimeField.TZ_OFFSET.search(value)
            if match:
                value, op, hours, minutes = match.groups()
                value = super(AppFormDateTimeField, self).to_python(value)
                value = value - datetime.timedelta(hours=int(op + hours), minutes=int(op + minutes))
                value = value.replace(tzinfo=timezone.TZ_UTC)
            else:
                raise
        
        if not isinstance(value, datetime.datetime):
            return value
        
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.TZ_DEFAULT)  #TZ_DEFAULTをセット.
        value = value.astimezone(timezone.TZ_DEFAULT) # TZ_DEFAULTにする.
        return value
    
class AppFormDateInput(forms.DateInput):
    input_type = 'date'
    def __init__(self, attrs=None, *args):
        attrs = attrs or {}
        if not attrs.has_key('width'):
            attrs.update(style='width:120px;')
        super(AppFormDateInput, self).__init__(attrs, *args)

class AppFormDateField(forms.DateField):
    """フォームの日付フィールド.
    """
    widget = AppFormDateInput
    
class AppDateField(models.DateField):
    """inputtypeをdateにしたい.
    """
    
    def __init__(self, *args, **kwgs):
        models.DateField.__init__(self, *args, **kwgs)
        
    __metaclass__ = models.SubfieldBase
    
    def formfield(self, **kwargs):
        defaults = {'form_class': AppFormDateField}
        defaults.update(kwargs)
        return super(AppDateField, self).formfield(**defaults)
    
class ObjectField(models.Field):
    '''
    PythonオブジェクトをシリアライズしてDBに格納するためのフィールド
    http://peta.okechan.net/blog/archives/1068
    '''
    __metaclass__ = models.SubfieldBase
    
    def db_type(self, connection):
        # mysql only...
        return 'BLOB'
    
    def to_python(self, value):
        """
        loadsしてみて成功したら結果を返す。
        失敗したらそのまま返す。
        つまりload可能な文字列オブジェクトはloadされてしまうためそのまま保存できない。
        """
        if isinstance(value, unicode):
            value = StrUtil.to_s(value)
        if isinstance(value, str):
            try:
                return cPickle.loads(value)
            except (cPickle.UnpicklingError, EOFError):
                return value
        return value
    
    def get_db_prep_save(self, value, connection):
        if value is None:
            return None
        return cPickle.dumps(value)

class NonObjectForeignKey(models.ForeignKey):
    """他のモデルとのリレーション用フィールド.
    普通に使うと値にリレーション対象のオブジェクトを返すのでintで返すようにする.
    """
    def get_attname(self):
        # デフォでDBカラム名がcolumn_name + '_id'になってしまうので.
        return self.name
    
    def label_from_instance(self, obj):
        return u'%s（id:%s）' % (obj.name, obj.id)
    def to_python(self, value):
        """
        勝手にオブジェクトに変換して整数じゃないとダメですとかで弾かれるので.
        """
        return value
