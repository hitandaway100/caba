# -*- coding: utf-8 -*-
import re
import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import DEFAULT_DB_ALIAS
from django.db.models.query import QuerySet, ValuesQuerySet
from platinumegg.app.cabaret.models.base import save_custom_retries


class Query:
    """SQL直叩き用.
    """
    regex_as = re.compile(r'as|AS')     # AS,asでﾌｨｰﾙﾄﾞを分割するための正規表現.
    
    def __init__(self, model_cls, query, query_values, using=settings.DB_DEFAULT):
        self.__model_cls = model_cls
        q = query
        i = 1
        for _ in query_values:
            q = q.replace(':%s' % i, '%s')
            i += 1
        self.__query = q
        self.__query_values = query_values
        self.__using = using
    
    def query_string(self, fields, limit=None, offset=0):
        q = 'SELECT %s FROM %s %s' % (fields, self.__model_cls.get_tablename(), self.__query)
        if limit != None:
            q += ' LIMIT %s,%s' % (offset, limit)
        return q
    
    #-------------------------------------------------------------
    # 実行.
    @staticmethod
    def __execute_sub(querystring, values, connection):
        cursor = connection.cursor()
        if querystring[-1] != ';':
            querystring += ';'
        cursor.execute(querystring, values)
        return cursor
    
    @staticmethod
    def execute_one(querystring, values, using=settings.DB_DEFAULT):
        from django.db import connections
        connection = connections[using]
        return Query.__execute_sub(querystring, values, connection).fetchone()
    
    @staticmethod
    def execute_all(querystring, values, using=settings.DB_DEFAULT):
        from django.db import connections
        connection = connections[using]
        return Query.__execute_sub(querystring, values, connection).fetchall()
    
    @staticmethod
    def execute_update(querystring, values, do_commit):
        connection = transaction.connections[DEFAULT_DB_ALIAS]
        Query.__execute_sub(querystring, values, connection)
        if do_commit:
            transaction.commit_unless_managed() # トランザクション中じゃなかったらコミット.
    
    def fetch(self, fields='*', limit=1000, offset=0):
        """
        """
        q = self.query_string(fields, limit, offset)
        return Query.execute_all(q, self.__query_values, self.__using)
        
    def get(self, fields='*'):
        """
        戻り値はﾀﾌﾟﾙです.
        """
        q = self.query_string(fields)
        try:
            return Query.execute_one(q, self.__query_values, self.__using)
        except ObjectDoesNotExist:
            return None

class PIQuerySet(QuerySet):
    """
    QuerySet.
    """
    def get(self, *args, **kwargs):
        try:
            return super(PIQuerySet, self).get(*args, **kwargs)
        except ObjectDoesNotExist:
            return None
    
    def fetch(self, limit=1000, offset=0):
        end = offset + limit
        return self.all()[offset:end]
    
    def fetch_all(self, offset=0):
        return self.all()[offset:]
    
    def values(self, *fields):
        return self._clone(klass=PIValuesQuerySet, setup=True, _fields=fields)
    
    def __update_sub(self, **kwargs):
        """updateの実際に書き込みを行っている部分.
        """
        return super(PIQuerySet, self).update(**kwargs)
    
    def update(self, **kwargs):
        if transaction.is_managed(using=self.db):
            # トランザクション中.
            return super(PIQuerySet, self).update(**kwargs)
        else:
            # トランザクション外.
            return save_custom_retries(self.__update_sub, **kwargs)
        
    def for_update(self):
        """ SELECT ~ FOR UPDATE なクエリで取得.
        https://coderanger.net/2011/01/select-for-update/
        """
        from django.db import connections
        if 'sqlite' in connections[self.db].settings_dict['ENGINE'].lower():
            # Noop on SQLite since it doesn't support FOR UPDATE
            return self
        sql, params = self.query.get_compiler(self.db).as_sql()
        return self.model._default_manager.raw(sql.rstrip() + ' FOR UPDATE', params)
        
class PIValuesQuerySet(ValuesQuerySet):
    """
    ValuesQuerySet.
    """
    def get(self, *args, **kwargs):
        try:
            return super(PIValuesQuerySet, self).get(*args, **kwargs)
        except ObjectDoesNotExist:
            return None
    
    def fetch(self, limit=1000, offset=0):
        end = offset + limit
        return self[offset:end]
    
    def fetch_all(self, offset=0):
        return self[offset:]

