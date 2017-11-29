# -*- coding: utf-8 -*-
from _mysql_exceptions import OperationalError
from copy import copy
from django.db import transaction
from django.db.utils import IntegrityError
from platinumegg.app.cabaret.models.base.queryset import Query
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.opensocial.util import OSAUtil
from sqlalchemy.exc import TimeoutError
import datetime
import settings
import sys
import time
from platinumegg.lib.apperror import AppError
from platinumegg.app.cabaret.models.base.models import BaseMaster
import operator
from platinumegg.lib.redis.client import Client as redisClient
from platinumegg.lib.redis import config
from platinumegg.lib.cache.localcache import localcache
from defines import Defines


#------------------------------------------------------------------------
# transaction..
def commit_manually(using=None):
    """transaction.commit_manuallyを修正.
    """
    def inner_commit_manually(func, db=None):
        def _commit_manually(*args, **kw):
            db = transaction.DEFAULT_DB_ALIAS
            conn_wrapper = transaction.connections[db]
            try:
                transaction.enter_transaction_management(using=db)
                transaction.managed(True, using=db)
                if conn_wrapper.connection == None:
                    conn_wrapper._cursor()
                conn_wrapper.connection.autocommit(False)
                return func(*args, **kw)
            finally:
                if conn_wrapper.connection != None:
                    conn_wrapper.connection.autocommit(True)
                transaction.leave_transaction_management(using=db)
                
        return transaction.wraps(func)(_commit_manually)
    
    if using is None:
        using = transaction.DEFAULT_DB_ALIAS
    if callable(using):
        return inner_commit_manually(using, transaction.DEFAULT_DB_ALIAS)
    return lambda func: inner_commit_manually(func, using)

@commit_manually
def transaction_sub(function, *args, **kwargs):
    """実際のtransactionはここ.
    """
    try:
        result = function(*args, **kwargs)
    except:
        transaction.rollback()
        raise
    transaction.commit()
    return result

DEFAULT_RETRY_COUNT = 3
def run_in_transaction(function, *args, **kwargs):
    return run_in_transaction_custom_retries(DEFAULT_RETRY_COUNT, function, *args, **kwargs)
    
def run_in_transaction_custom_retries(retry, function, *args, **kwargs):
    MYSQL_WAIT_MAX = 3
    
    count = retry
    start_time = OSAUtil.get_now()
    while True:
        try:
            return transaction_sub(function, *args, **kwargs)
        except AppError:
            # apperrorは意図的に出しているからｽﾙｰ.
            raise
        except CabaretError:
            # apperrorは意図的に出しているからｽﾙｰ.
            raise
        except TimeoutError:
            # db接続ﾀｲﾑｱｳﾄ.
            raise
        except OperationalError:
            # mysqlの接続等のエラー.
            now = OSAUtil.get_now()
            dif = now - start_time
            if dif.seconds < MYSQL_WAIT_MAX:
                time.sleep(0.1)
            else:
                info = sys.exc_info()
                trace = CabaretError.makeErrorTraceString(info)
                raise CabaretError(trace, CabaretError.Code.TOO_MANY_TRANSACTION)
        except:
            if count <= 0:
                raise
            count -= 1
            time.sleep(0.01)

#------------------------------------------------------------------------------
# etc..
class ModelRequestMgr:
    """なんかここでDBへのﾘｸｴｽﾄをまとめたい.
    """
    def __init__(self, loginfo=None):
        self.__save_models = {}         # saveするモデル.
        self.__save_model_keys = []
        self.__delete_models = {}       # 消すモデル.
        
        self.__saved_models = {}        # saveが終わったモデル.
        self.__deleted_models = {}      # 消したモデル.
        
        self.__insert_model_count = 0   # インサートするモデルの番号.オートインクリメントのモデルはID決まってないので.
        self.__querys = []              # 直打ちのクエリ.
        
        self.__got_models = {}  # 取得済みのモデル.
        self.__requested_keys = {}
        for k in settings.DATABASES.keys():
            self.__got_models[k] = {}
            self.__requested_keys[k] = {}
        
        self.__got_models_forupdate = {}    # 取得済みのモデル.
        
        self.__write_end_methods = []   # 書き込み終了後に実行したいメソッド.[method, args]
        self.__for_update_tasks = []    # For Updateで操作するタスク.
        
        self.__localcache = localcache.Client()
        
        if loginfo is None:
            loginfo = lambda x:None
        self.addloginfo = loginfo
    
    def __reset_requested_keys(self):
        """DBにリクエストをなげたフラグをリセット.
        """
        for k in settings.DATABASES.keys():
            self.__requested_keys[k] = {}
    
    def __get_requested_keys(self, model_cls, using):
        """DBにリクエストをなげたフラグをリセット.
        """
        modelname = model_cls.__name__
        data = self.__requested_keys[using][modelname] = self.__requested_keys[using].get(modelname) or set([])
        return data
    
    def __add_requested_keys(self, model_cls, using, keys):
        """DBにリクエストをなげたフラグをリセット.
        """
        modelname = model_cls.__name__
        self.__requested_keys[using][modelname] = self.__get_requested_keys(model_cls, using) | set(keys)
    
    def need_write(self):
        # 書きこむ必要があるか.
        return len(self.__delete_models) or len(self.__save_models) or len(self.__querys)
    
    def __make_key(self, model_cls, p_key):
        """溜め込んだﾓﾃﾞﾙの識別子.
        """
        if p_key is None:
            p_key = 'NewModel:%s' % self.__insert_model_count
            self.__insert_model_count += 1
        return '%s:%s' % (model_cls.__name__, p_key)
    
    def set_got_models(self, modellist, using=None):
        """取得済みのモデルを溜め込んでおく.
        """
        for model in modellist:
            current_db = using or model.current_db
            got_models = self.__got_models[current_db] = self.__got_models.get(current_db) or {}
            key = self.__make_key(model.__class__, model.key())
            got_models[key] = model
    
    def set_got_models_forupdate(self, modellist):
        """取得済みのモデルを溜め込んでおく.
        """
        for model in modellist:
            key = self.__make_key(model.__class__, model.key())
            self.__got_models_forupdate[key] = model
    
    def get_models(self, model_cls, p_keys, get_instance=False, using=settings.DB_DEFAULT, *args, **kwargs):
        """まとめて取得できる所はなるべくこれで。
        """
        self.addloginfo(u'get_models: %s:%s' % (model_cls.__name__, p_keys))
        got_models = self.__got_models[using] = self.__got_models.get(using) or {}
        
        
        ret_objs = []
        req_p_keys = []
        for p_key in p_keys:
            key = self.__make_key(model_cls, p_key)
            obj = got_models.get(key, None)
            if obj is None:
                req_p_keys.append(p_key)
            else:
                ret_objs.append(obj)
        
        cnt_from_already = len(ret_objs)
        cnt_from_cache = 0
        cnt_from_db = 0
        if 0 < len(req_p_keys):
            cached_models = self.__get_models_from_cache(model_cls, req_p_keys, using)
            
            if get_instance:
                requested_keys = set([])
            else:
                requested_keys = self.__get_requested_keys(model_cls, using)
            
            cnt_from_cache = len(req_p_keys)
            req_p_keys = list(set(req_p_keys) - set(cached_models.keys()) - requested_keys)
            obj_list = filter(lambda x:x != 'None', cached_models.values())
            
            cnt_from_db = len(req_p_keys)
            cnt_from_cache -= cnt_from_db
            
            if 0 < cnt_from_db:
                if get_instance:
                    db_models = model_cls.getInstanceByKey(req_p_keys, *args, **kwargs)
                else:
                    db_models = model_cls.getByKey(req_p_keys, *args, **kwargs)
                if db_models:
                    self.__save_models_to_cache(db_models)
                    obj_list.extend(db_models)
                if len(req_p_keys) != len(db_models):
                    not_found_keys = list(set(req_p_keys) - set([model.key() for model in db_models]))
                    for not_found_key in not_found_keys:
                        self.__save_models_to_cache_for_none(model_cls, not_found_key)
                
                self.__add_requested_keys(model_cls, using, req_p_keys)
            
            self.set_got_models(obj_list, using=using)
            ret_objs.extend(obj_list)
        self.addloginfo(u'get_models end:db=%d,cache=%d,already=%d' % (cnt_from_db,cnt_from_cache,cnt_from_already))
        return ret_objs
    
    def get_model(self, model_cls, p_key, get_instance=False, using=settings.DB_DEFAULT, *args, **kwargs):
        """モデルを取得済みだったら以前とったものを返す.
        未取得だったらgetByID(p_key)でモデルを取得.
        get_instance=True だったらgetInstanceByID(p_key)で取得.
        """
        datalist = self.get_models(model_cls, [p_key], get_instance, using)
        if 0 < len(datalist):
            return datalist[0]
        else:
            return None
    
    def get_models_forupdate(self, model_cls, p_keys, *args, **kwargs):
        """forupdateで取得.
        これはあまりおすすめしない.
        """
        got_models = self.__got_models_forupdate
        
        ret_objs = []
        req_p_keys = []
        for p_key in p_keys:
            key = self.__make_key(model_cls, p_key)
            obj = got_models.get(key, None)
            if obj is None:
                req_p_keys.append(p_key)
            else:
                ret_objs.append(obj)
        if 0 < len(req_p_keys):
            if len(req_p_keys) == 1:
                obj = model_cls.getByKeyForUpdate(req_p_keys[0], *args, **kwargs)
                obj_list = [obj] if obj else []
            else:
                obj_list = model_cls.fetchByKeyForUpdate(req_p_keys, *args, **kwargs)
            self.set_got_models_forupdate(obj_list)
            ret_objs.extend(obj_list)
        return ret_objs
    
    def get_model_forupdate(self, model_cls, p_key, *args, **kwargs):
        """モデルを取得済みだったら以前とったものを返す.
        未取得だったらgetByID(p_key)でモデルを取得.
        get_instance=True だったらgetInstanceByID(p_key)で取得.
        """
        datalist = self.get_models_forupdate(model_cls, [p_key], *args, **kwargs)
        if 0 < len(datalist):
            return datalist[0]
        else:
            return None
    
    def save_mastermodel_keyset(self, modellist, reflesh=False):
        """テーブルの全取得用のキーのセットを保存.
        """
        redisdb = redisClient.get(config.REDIS_CACHE)
        dic = {}
        pipe = redisdb.pipeline()
        for model in modellist:
            if not isinstance(model, BaseMaster):
                raise CabaretError(u'これはマスターデータではありません')
            key = 'mastermodel_keyset::%s:%d' % (model.__class__.get_tablename(), int(model.is_public))
            if not dic.has_key(key):
                dic[key] = []
                if reflesh:
                    pipe.delete(key)
            dic[key].append(model.pkey_to_str(model.key()))
        for k, arr in dic.items():
            for v in arr:
                pipe.sadd(k, v)
        pipe.execute()
    
    def __get_mastermodel_list(self, model_cls, idlist=False, fetch_deleted=False, using=settings.DB_READONLY, reflesh=False):
        """テーブルのデータをすべて取得.
        """
        redisdb = redisClient.get(config.REDIS_CACHE)
        keys = [
            ('mastermodel_keyset::%s:%d' % (model_cls.get_tablename(), int(True)), Defines.PublishStatus.OPEN_STATAS_LIST)
        ]
        if fetch_deleted:
            keys.append(('mastermodel_keyset::%s:%d' % (model_cls.get_tablename(), int(False)), Defines.PublishStatus.CLOSED_STATAS_LIST))
        
        result = []
        for k,pubstatus in keys:
            if not reflesh and redisdb.exists(k):
                modelidlist = [model_cls.str_to_pkey(pk) for pk in redisdb.smembers(k)]
                if idlist:
                    result.extend(modelidlist)
                else:
                    modellist = self.get_models(model_cls, modelidlist, using=using)
                    result.extend(modellist)
            else:
                filters = {
                    '%s__in' % Defines.PUBLISH_STATUS_COLUMN : pubstatus,
                }
                modellist = model_cls.fetchValues(filters=filters, fetch_deleted=True, using=using)
                
                self.save_mastermodel_keyset(modellist, True)
                self.set_got_models(modellist)
                if idlist:
                    result.extend([model.key() for model in modellist])
                else:
                    result.extend(modellist)
        return result
    
    def get_mastermodel_idlist(self, model_cls, order_by=None, fetch_deleted=False, using=settings.DB_READONLY, reflesh=False):
        """テーブルのデータのIDをすべて取得.
        """
        result = self.__get_mastermodel_list(model_cls, idlist=True, fetch_deleted=fetch_deleted, using=using, reflesh=reflesh)
        return result
    
    def get_mastermodel_all(self, model_cls, order_by=None, fetch_deleted=False, using=settings.DB_READONLY, reflesh=False):
        """テーブルのデータをすべて取得.
        """
        result = self.__get_mastermodel_list(model_cls, fetch_deleted=fetch_deleted, using=using, reflesh=reflesh)
        if order_by:
            reverse = order_by[0] == '-'
            if reverse:
                order_by = order_by[1:]
            result.sort(key=operator.attrgetter(order_by), reverse=reverse)
        return result
    
    def get_mastermodel_count(self, model_cls, fetch_deleted=False, using=settings.DB_READONLY, reflesh=False):
        """モデル数を検索.
        """
        result = self.__get_mastermodel_list(model_cls, idlist=True, fetch_deleted=fetch_deleted, using=using, reflesh=reflesh)
        return len(result)
    
    def set_save(self, model, fields=None, saved_task=None, saved_task_args=None):
        """saveするモデルに追加.
        """
        if model.current_db != settings.DB_DEFAULT:
            raise CabaretError('Invalid database!! %s:%s' % (model.__class__.__name__, model.current_db))
        
        data = self.__get_save_reserved(model)
        update_fields = data['fields']
        if fields is None:
            # 全部更新.
            data['fields'] = None
        elif update_fields is not None:
            # 更新するフィールドを追加.
            data['fields'] = list(set(update_fields + fields))
        if saved_task:
            data['saved_task'].append((saved_task, saved_task_args or []))
        self.addloginfo(u'set_save: %s : %s' % (model.__class__.__name__, update_fields))
    
    def __get_save_reserved(self, model):
        # 更新予約に入ってるデータを取得.
        key = self.__make_key(model.__class__, model.key())
        data = self.__save_models.get(key, None)
        if data is None:
            if self.__delete_models.get(key, None) is not None:
                raise CabaretError(u'削除予約に入ってる:%s' % key)
            data = {
                'db':model,
                'fields':[],
                'adding':model._state.adding, # djangoのaddingはinsertのtransactionでこけるとFalseにしちゃうので独自で持つ.
                'saved_task' : [],
            }
            self.__save_models[key] = data
            if not key in self.__save_model_keys:
                self.__save_model_keys.append(key)
        return data
    
    def set_delete(self, model):
        """削除するモデルに追加.
        """
        key = self.__make_key(model.__class__, model.key())
        data = self.__delete_models.get(key, None)
        if data is None:
            if self.__save_models.get(key, None) is not None:
                raise CabaretError(u'更新予約に入ってる')
            self.__delete_models[key] = model
        self.addloginfo(u'set_delete: %s' % model.__class__.__name__)
    
    def set_query(self, query):
        """直打ち.
        """
        if query:
            self.__querys.append(query)
    
    def add_forupdate_task(self, model_cls, p_key, method, *args, **kwargs):
        """トランザクション内で行うforUpdateタスクを詰む.
        method:
            引数:
                model           対象のモデル.
                inserted        INSERTされたときTrue.
                *args,**kwargs
            戻り値:
                更新するフィールドのリスト.
        
        DBに無いデータをfor updateで取ろうとすると良くないので
        ない場合はinsert予約に入れる.
        """
        obj = self.__got_models.get(self.__make_key(model_cls, p_key), None)
        if obj is None:
            cnt = model_cls.count({model_cls.get_primarykey_column():p_key})
            if cnt == 0:
                obj = self.get_model(model_cls, p_key, get_instance=True)
                if obj._state.adding:
                    self.set_save(obj)
        task = (model_cls, p_key, method, args, kwargs)
        self.__for_update_tasks.append(task)
    
    def add_write_end_method(self, func, *args, **kwargs):
        self.__write_end_methods.append((func, args, kwargs))
    
    def write_all(self, handler=None):
        """モデルを全て書き込み.
        """
        def log(txt):
            self.addloginfo(txt)
        
        log(u'write_all start')
        
        insert_models = {} # インサートするのをテーブルごとにまとめたい。。
        
        for key in self.__save_model_keys:
            data = self.__save_models[key]
            update_fields = data['fields']
            model = data['db']
            adding = data['adding']
            saved_tasks = data['saved_task']
            if adding:
                try:
                    model.insert()
                except IntegrityError, e:
                    if -1 < str(e).find('Duplicate entry'):
                        model.update()
                    else:
                        raise e
                # insertしたモデルに追加.
                insert_models[key] = model
            else:
                updatable_columns = model.get_updatable_column_names()
                if update_fields is not None:
                    update_fields = list(set(update_fields) & set(updatable_columns))
                else:
                    update_fields = updatable_columns
                model.update(update_fields)
            
            for saved_task, saved_task_args in saved_tasks:
                saved_task(model, *saved_task_args)
            
            log(u'write_all write model: %s : %s' % (model.__class__.__name__, update_fields))
            
        self.__saved_models = self.__save_models.copy()
        
        tmp = {}
        for key, model in self.__delete_models.items():
            self.__deleted_models[key] = model
            data = tmp[model.__class__.__name__] = tmp.get(model.__class__.__name__) or {'cls':model.__class__,'id':[]}
            data['id'].append(model.key())
        
        for data in tmp.values():
            model_cls = data['cls']
            filters = {}
            filters['%s__in' % model_cls.get_primarykey_column()] = data['id']
            model_cls.all().filter(**filters).delete()
        
        log(u'write_all delete all')
        
        for query in self.__querys:
            Query.execute_update(query, [], False)
        
        log(u'write_all execute update all')
        
        # For Updateで行うタスク.
        for_update_models = {}
        for task in self.__for_update_tasks:
            model_cls, p_key, method, args, kwargs = task
            key = self.__make_key(model_cls, p_key)
            obj = insert_models.get(key, None)
            
            inserted = obj is not None
            if inserted and self.__deleted_models.has_key(key):
                # insert直後にdeleteを呼んでいる.これはdeadlockの危険があるのでやめて...
                raise CabaretError('There is a risk of deadlock....model=%s, p_key=%s' % (model_cls.__name__, p_key))
            
            data = for_update_models.get(key, {'db':None,'fields':[]})
            
            obj = obj or data['db'] or self.get_model_forupdate(model_cls, p_key)
            if obj is None:
                # ここでNoneなのは上のチェックで引っかかるのよりまずい気がする.
                raise CabaretError('Next key lock!! %s, p_key=%s' % (model_cls.__name__, p_key))
            obj_copy = copy(obj)
            fields = method(obj, inserted, *args, **kwargs)
            
            if obj.key() is None:   # 消されたっぽい.
                self.__deleted_models[key] = obj_copy
            else:
                data['db'] = obj
                if fields is not None and data['fields'] is not None:
                    data['fields'] += fields
                elif inserted:
                    data['fields'] = None
                else:
                    data['fields'] = obj.get_updatable_column_names()
                for_update_models[key] = data
        
        for key, data in for_update_models.items():
            model = data['db']
            fields = data['fields']
            
            if fields is not None:
                updatable_columns = model.get_updatable_column_names()
                fields = list(set(fields) & set(updatable_columns))
                model.update(fields)
            else:
                model.update()
            
            self.__saved_models[key] = data
        
        self.__save_models = {}
        self.__save_model_keys = []
        self.__delete_models = {}
        self.__for_update_tasks = []
        
        # 取得済みフラグを破棄.
        self.__reset_requested_keys()
        
        log(u'write_all execute for_update all')
    
    def write_end(self):
        """モデルの書き込み終わりました。
        """
        multi_dict = {}
        
        for data in self.__saved_models.values():
            model = data['db']
            model_clsname = model.__class__.__name__
            dic = multi_dict[model_clsname] = multi_dict.get(model_clsname) or {'models':{},'ttl':model.__class__.get_cache_ttl()}
            dic['models'][model.pkey_to_str(model.key())] = model
        
        for dic in multi_dict.values():
            self.__save_models_to_cache(dic['models'].values(), dic['ttl'], True)
        
        multi_dict = {}
        for model in self.__deleted_models.values():
            model_clsname = model.__class__.__name__
            dic = multi_dict[model_clsname] = multi_dict.get(model_clsname) or {'cls':model.__class__, 'models':{}}
            dic['models'][model.key()] = model
        
        for dic in multi_dict.values():
            self.delete_models_from_cache(dic['cls'], dic['models'].keys())
        
        # モデルインスタンスの持っているwrite_end_method.
        inited_method_keys = []
        for data in self.__saved_models.values():
            model = data['db']
            mothodset = model.get_write_end_methods()
            if not mothodset:
                continue
            for method_key, method_set in mothodset.items():
                if method_key in inited_method_keys:
                    continue
                if 2 < len(method_set):
                    kwgs = method_set[2]
                else:
                    kwgs = {}
                method_set[0](*method_set[1], **kwgs)
        
        # 独自に追加したwrite_end_method.
        for method, args, kwargs in self.__write_end_methods:
            method(*args, **kwargs)
        
    
    def get_wrote_model(self, model_cls, p_key, method=None, *args, **kwargs):
        """書き込みが終わったモデルを取得.
        無ければ取ってくる.
        """
        key = self.__make_key(model_cls, p_key)
        model = self.__saved_models.get(key, {}).get('db', None)
        if model is None and method is not None:
            model = method(*args, **kwargs)
        return model
    
    def get_wrote_models(self):
        # 書き込み終わったモデル全部取得.
        return self.__saved_models
    
    def get_deleted_models(self):
        # 削除が終わったモデル全部取得.
        return self.__deleted_models
    
    @staticmethod
    def __to_query_value(value):
        # クエリに使える値にする。
        if value is None:
            value = u'NULL'
        elif isinstance(value, datetime.datetime):
            value = u'"%04d-%02d-%02d %02d:%02d:%02d"' % (value.year, value.month, value.day, value.hour, value.minute, value.second)
        elif isinstance(value, bool):
            if value:
                value = u'true'
            else:
                value = u'false'
        elif isinstance(value, int):
            value = u'%s' % value
        else:
            value = u'"%s"' % value
        return value
    
    #=====================================================================
    # キャッシュ.
    def __get_models_from_cache(self, model_cls, p_keys, using):
        """キャッシュから取得.
        """
        if issubclass(model_cls, BaseMaster):
            return self.__get_models_from_cache_for_master(model_cls, p_keys, using)
        else:
            return self.__get_models_from_cache_default(model_cls, p_keys, using)
    
    def __get_models_from_cache_default(self, model_cls, p_keys, using):
        """キャッシュから取得(デフォルト).
        """
        if using == settings.DB_READONLY and model_cls.__name__ != 'PlayerRequest':
            client = OSAUtil.get_cache_client()
            namespace = model_cls.__name__
            return client.mget(p_keys, namespace)
        else:
            return {}
    
    def __get_models_from_cache_for_master(self, model_cls, p_keys, using):
        """キャッシュから取得(マスター用).
        """
        return self.__localcache.get_many(p_keys, model_cls.__name__)
    
    def save_models_to_cache(self, modellist):
        """キャッシュに保存.
        """
        self.__save_models_to_cache(modellist)
    
    def __save_models_to_cache(self, modellist, ttl=None, is_update=False):
        """キャッシュに保存.
        """
        datadict = {}
        for model in modellist:
            if isinstance(model, BaseMaster):
                self.__save_models_to_cache_for_master(model, is_update)
            else:
                namespace = model.__class__.__name__
                dic = datadict[namespace] = datadict.get(namespace) or {}
                dic[model.key()] = model
        
        for namespace,modeldict in datadict.items():
            self.__save_models_to_cache_default(modeldict, namespace, ttl)
    
    def __save_models_to_cache_default(self, modeldict, namespace, ttl):
        """キャッシュに保存(デフォルト).
        """
        client = OSAUtil.get_cache_client()
        client.mset(modeldict, time=ttl, namespace=namespace)
    
    def __save_models_to_cache_for_master(self, model, is_update):
        """キャッシュに保存(マスター用).
        """
        if is_update:
            self.__localcache.delete(model.key(), model.__class__.__name__)
        else:
            self.__localcache.set(model.key(), model, model.get_class_name())
    
    def __save_models_to_cache_for_none(self, model_cls, key, ttl=None):
        """キャッシュに保存(NoneType用).
        """
        client = OSAUtil.get_cache_client()
        namespace = model_cls.__name__
        client.set(key, 'None', namespace=namespace)
    
    def delete_models_from_cache(self, model_cls, p_keys):
        """キャッシュから削除.
        """
        if issubclass(model_cls, BaseMaster):
            self.__delete_models_to_cache_for_master(model_cls, p_keys)
        else:
            self.__delete_models_to_cache_default(model_cls, p_keys)
    
    def __delete_models_to_cache_default(self, model_cls, keys):
        """キャッシュから削除(デフォルト).
        """
        client = OSAUtil.get_cache_client()
        namespace = model_cls.__name__
        client.mdelete(keys, namespace)
    
    def __delete_models_to_cache_for_master(self, model_cls, keys):
        """キャッシュから削除(マスター用).
        """
        self.__localcache.delete_many(keys, model_cls.__name__)
    
