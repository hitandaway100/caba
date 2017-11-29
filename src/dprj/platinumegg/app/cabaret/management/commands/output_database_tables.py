# -*- coding: utf-8 -*-
import inspect
from collections import namedtuple
from django.core.management.base import BaseCommand
from django.db import models, connections
from django.db.utils import DEFAULT_DB_ALIAS
from django.db.models.fields import NOT_PROVIDED
import settings_sub
import os
from mako.template import Template
from platinumegg.app.cabaret import models as mymodels
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.csvutil import CSVWriter
from platinumegg.lib.strutil import StrUtil
from platinumegg.lib.pljson import Json
import shutil

db_master = DEFAULT_DB_ALIAS
connection = connections[db_master]

class Command(BaseCommand):
    """modelsに並べたモデルの設計書みたいなものを出力する.
    出力方法はhtml,csv,json
    """
    
    ModelParam = namedtuple('ModelParam', 'name,description,fields')
    FieldParam = namedtuple('FieldParam', 'name,db_type,indexes,auto_increment,null,default,verbose_name,help_text')
    
    def handle(self, *args, **options):
        
        print '================================'
        print 'output_database_tables'
        print '================================'
        
        msg = 'Please select the output format from the following.\n'
        msg += '[html, csv, json]\n'
        msg += 'test name:'
        targetname = raw_input(msg).lower()
        f = getattr(self, 'output_{}'.format(targetname), None)
        if f is None:
            print 'Invalid format...{}'.format(targetname)
            return
        
        # モデルのクラスのリスト.
        model_cls_list = self.__get_model_cls_list()
        # モデルのパラメータ化.
        model_param_list = [self.__get_model_cls_param(model_cls) for model_cls in model_cls_list]
        
        # 出力先.
        if not os.path.exists(settings_sub.TMP_DOC_ROOT):
            os.mkdir(settings_sub.TMP_DOC_ROOT)
        output_dir = os.path.join(settings_sub.TMP_DOC_ROOT, '{}_{}'.format(settings_sub.APP_NAME, targetname))
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        
        # ディレクトリ作成.
        os.mkdir(output_dir)
        
        f(output_dir, model_param_list)
        
        print 'all done...'
    
    def output_html(self, output_dir, model_param_list):
        """htmlを出力.
        """
        def write_html(template, htmlname, **kwargs):
            html = Template(template, default_filters=['decode.utf8'], output_encoding='utf-8', input_encoding='utf-8').render_unicode(**kwargs).encode('utf-8', 'replace')
            self.write_file(os.path.join(output_dir, htmlname), html)
            print 'write...{}'.format(os.path.join(output_dir, htmlname))
        
        # indexページ.
        write_html(MODEL_INDEX_TEMPLATE_HTML, 'index.html', app_title=settings_sub.APP_TITLE, model_param_list=model_param_list)
        
        # 各モデルのHTML.
        for model_param in model_param_list:
            write_html(MODEL_TEMPLATE_HTML, '{}.html'.format(model_param.name), model_param=model_param)
        
        print 'Output html...{}'.format(output_dir)
    
    def output_json(self, output_dir, model_param_list):
        """jsonを出力.
        """
        json_data = {}
        for model_param in model_param_list:
            fields = [field._asdict() for field in model_param.fields]
            model_param_dict = model_param._asdict()
            model_param_dict['fields'] = fields
            json_data[model_param.name] = model_param_dict
        json = Json.encode(json_data)
        
        filepath = os.path.join(output_dir, 'tables.json')
        self.write_file(filepath, StrUtil.to_s(json))
        
        print 'Output json...{}'.format(output_dir)
    
    def output_csv(self, output_dir, model_param_list):
        """csvを出力.
        """
        columns = (
            (u'カラム名(物理名)', lambda field_param:field_param.name),
            (u'型', lambda field_param:field_param.db_type),
            (u'INDEX', lambda field_param:','.join(field_param.indexes)),
            (u'AUTO_INCREMENT', lambda field_param:u'◯' if field_param.auto_increment else u''),
            (u'NULL', lambda field_param:u'◯' if field_param.null else u''),
            (u'デフォルト値', lambda field_param:field_param.default),
            (u'カラム名(論理名)', lambda field_param:field_param.verbose_name),
            (u'補足', lambda field_param:field_param.help_text),
        )
        
        for model_param in model_param_list:
            filepath = os.path.join(output_dir, '{}.csv'.format(model_param.name))
            csv = CSVWriter(filepath)
            csv.add([u'#{}'.format(model_param.name)])
            csv.add([u'#{}'.format(StrUtil.to_u(model_param.description))])
            csv.add([column_name for column_name, _ in columns])
            
            for field in model_param.fields:
                csv.add([column_value_gettr(field) for _, column_value_gettr in columns])
            csv.output()
            print 'write...{}'.format(filepath)
        
        print 'Output csv...{}'.format(filepath)
    
    def __get_model_cls_list(self):
        """モデルのクラスのリスト.
        """
        arr = []
        for v in mymodels.__dict__.values():
            if not hasattr(v, '__bases__'):
                # クラスじゃない.
                continue
            elif not models.Model in inspect.getmro(v):
                # モデルじゃない.
                continue
            elif v._meta.abstract:
                # 仮想クラスのモデル.
                continue
            arr.append(v)
        return arr
    
    def __get_model_cls_param(self, model_cls):
        """モデルを構成するパラメータを取得.
        """
        # テーブル名.
        name = model_cls._meta.db_table
        
        # テーブルの説明.
        description = inspect.getdoc(model_cls)
        
        # カラム.
        fieldparams = [self.__get_field_param(field) for field in model_cls._meta.fields]
        fieldparam_dict = dict([(fieldparam.name, fieldparam) for fieldparam in fieldparams])
        
        # 複合インデクス.
        def set_multi_index(multi_indexes, basename):
            if multi_indexes:
                for index_fields in multi_indexes:
                    index_name = '{}({})'.format(basename, ','.join(index_fields))
                    for fieldname in index_fields:
                        fieldparam = fieldparam_dict[fieldname]
                        fieldparam.indexes.append(index_name)
        set_multi_index(model_cls._meta.unique_together, 'unique')
        set_multi_index(model_cls._meta.index_together, 'index')
        
        return self.ModelParam(name, description, fieldparams)
    
    def __get_field_param(self, field):
        """フィールドを構成するパラメータを取得.
        """
        # カラム名.
        name = field.name
        verbose_name = field.verbose_name
        
        db_type_arr = field.db_type(connection).lower().split(' ')
        
        # auto_increment.
        if 'auto_increment' in db_type_arr:
            auto_increment = True
            db_type_arr.remove('auto_increment')
        else:
            auto_increment = False
        
        # 型.
        db_type = ' '.join(db_type_arr)
        
        # null.
        null = field.null
        
        # デフォルト値.
        if field.default == NOT_PROVIDED:
            default = ''
        elif field.default == OSAUtil.get_now:
            # 現在時刻.
            default = 'NOW()'
        else:
            default = field.get_default()
        
        # インデクス.
        indexes = []
        if field.primary_key:
            indexes.append('primary')
        elif field.unique:
            indexes.append('unique({})'.format(field.name))
        elif field.db_index:
            indexes.append('index({})'.format(field.name))
        
        # カラムの説明.
        help_text = field.help_text
        
        return self.FieldParam(name, db_type, indexes, auto_increment, null, default, verbose_name, help_text)
    
    def write_file(self, filepath, v):
        f = None
        try:
            f = open(filepath, "w")
            f.write(v)
        finally:
            if f:
                f.close()

MODEL_INDEX_TEMPLATE_HTML = """<html><body>
<b>${app_title}</b>
<table border="1" width="320px">
    %for model_param in model_param_list:
        <tr><td><a href="${model_param.name}.html">${model_param.name}</a></td></tr>
    %endfor
</table>
</body></html>"""

MODEL_TEMPLATE_HTML = """<html><body>
<table border="1">
    <tr><td width="100px">テーブル名(論理名)</td><td width="320px">${model_param.name}</td></tr>
    <tr><td width="100px">説明</td><td width="320px">${model_param.description | h}</td></tr>
    <tr><td width="100px">制約</td><td width="320px"></td></tr>
</table>
<br />
<table border="1">
    <tr>
        <td width="160px">カラム名(物理名)</td>
        <td width="160px">型</td>
        <td width="200px">INDEX</td>
        <td width="120px">AUTO_INCREMENT</td>
        <td width="60px">NULL</td>
        <td width="100px">デフォルト値</td>
        <td width="180px">カラム名(論理名)</td>
        <td width="200px">補足</td>
    </tr>
    %for field_param in model_param.fields:
        <tr>
            <td>${field_param.name}</td>
            <td>${field_param.db_type}</td>
            <td>${','.join(field_param.indexes)}</td>
            <td>${'◯' if field_param.auto_increment else ''}</td>
            <td>${'◯' if field_param.null else ''}</td>
            <td>${field_param.default}</td>
            <td>${field_param.verbose_name | h}</td>
            <td>${field_param.help_text | h}</td>
        </tr>
    %endfor
</table>
<div>
    <a href="index.html">一覧へ</a>
</div>
</body></html>"""


