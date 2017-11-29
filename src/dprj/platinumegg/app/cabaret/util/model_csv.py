# -*- coding: utf-8 -*-
import datetime
import os
import MySQLdb
from optparse import isbasestring
from platinumegg.lib.strutil import StrUtil
from platinumegg.app.cabaret.models.base.fields import ObjectField


class ModelCSVManager:
    """モデルをCSVに直します.
    """
    STR_KUGIRI = ','
    SIZE_MAX = 100000
    
    def __init__(self, dir_name):
        self.__model_table = {}
        self.__cls_table = {}
        self.__cls_name = []
        self.__mode = {}
        self.__dir_name = dir_name
        try:
            os.makedirs(dir_name)
        except:
            pass
    
    def __add_model(self, model):
        """モデルをCSV文字列に変換.
        """
        model_cls = model.__class__
        cls_name = model_cls.__name__
        
        tar_model_table = self.__model_table.get(cls_name, None)
        if tar_model_table is None:
            # 新規登録.
            self.__model_table[cls_name] = ''
            # ﾓﾃﾞﾙのクラスを登録.
            if self.__cls_table.get(cls_name) is None:
                self.__cls_table[cls_name] = model_cls
                self.__cls_name.append(cls_name)
        
        csv_data_list = []
        for field in model_cls._meta.fields:
            # フィールドに設定されている値.
            value = getattr(model, field.attname)
            if isinstance(field, ObjectField):
                value = field.get_db_prep_save(value, None)
            
            if value is None:
                value = 'NULL'
            elif isinstance(value, datetime.datetime):
                value = "%04d-%02d-%02d %02d:%02d:%02d" % (value.year, value.month, value.day, value.hour, value.minute, value.second)
            elif isinstance(value, bool):
                value = int(value)
            elif isbasestring(value):
                # 無理やりだけどﾊﾞｲﾅﾘﾃﾞｰﾀをｴｽｹｰﾌﾟ.
                value = MySQLdb.escape_string(StrUtil.to_s(value))
            csv_data_list.append('"%s"' % value)
        
        # 書き込む.
        csv_text = ModelCSVManager.STR_KUGIRI.join(csv_data_list) + '\r\n'
        self.__model_table[cls_name] += csv_text
        if ModelCSVManager.SIZE_MAX <= len(self.__model_table[cls_name]):
            return True
        else:
            return False
    
    def __write(self, csv_dict):
        """書き込む.
        """
        for cls_name,csv_text in csv_dict.items():
            if csv_text is None:
                continue
            mode = self.__mode.get(cls_name, "w")
            f = None
            try:
                filename = '%s/%s.csv' % (self.__dir_name, cls_name)
                f = open(filename, mode)
                f.write(csv_text)
                f.close()
                f = None
                self.__mode[cls_name] = "a"
            except:
                if f is not None:
                    f.close()
                raise
    
    def setModel(self, model):
        """モデルを設定.
        """
        model_cls = model.__class__
        cls_name = model_cls.__name__
        if self.__add_model(model):
            self.__write({cls_name:self.__model_table[cls_name]})
            self.__model_table[cls_name] = None
    
    def setModelList(self, model_list):
        """いちいち書くの面倒だからまとめて設定.
        """
        for model in model_list:
            if model is not None:
                self.setModel(model)
    
    def csv(self):
        pass
    
    def output(self):
        """sqlの書き出し.
        """
        if self.__model_table:
            self.__write(self.__model_table)
            self.__model_table = {}
        
        SQL_BASE = "load data local infile \"./%s.csv\" into table %s fields terminated by '"+ModelCSVManager.STR_KUGIRI+"' enclosed by '\"' escaped by '\\\\' LINES TERMINATED BY '\\r\\n' (%s);"
        sql_list = []
        for cls_name in self.__cls_name:
            model_cls = self.__cls_table[cls_name]
            column_names = u'`' + u'`,`'.join([field.attname for field in model_cls._meta.fields]) + u'`'
            sql_list.append(SQL_BASE % (cls_name, model_cls.get_tablename(), column_names))
        
        f = None
        try:
            filename = '%s/make_dummy_user.sql' % self.__dir_name
            f = open(filename, 'w')
            f.write('\n'.join(sql_list))
        finally:
            if f is not None:
                f.close()
            f = None
        
