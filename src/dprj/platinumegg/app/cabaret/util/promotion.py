# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.promotion.koihime import PromotionPrizeMasterKoihime,\
    PromotionRequirementMasterKoihime, PromotionDataKoihime,\
    PromotionConfigKoihime
from platinumegg.lib.thread import ThreadMethod
import urllib
from platinumegg.lib.opensocial.util import OSAUtil
import urllib2
from platinumegg.lib.pljson import Json
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from platinumegg.lib.cache.localcache import localcache
import datetime
from platinumegg.lib.opensocial.useragent import UserAgent
from platinumegg.app.cabaret.models.promotion.csc import PromotionConfigCsc,\
    PromotionPrizeMasterCsc, PromotionRequirementMasterCsc, PromotionDataCsc

class PromotionSettings:
    
    class Apps:
        KOIHIME = 'Koihime'
        CSC = 'Csc'
        STANDARD = 'Standard'

    class ModelClsSet():
        def __init__(self, config_cls, prizemaster_cls, requirementmaster_cls, userdata_cls):
            self.__config_cls = config_cls
            self.__prizemaster_cls = prizemaster_cls
            self.__requirementmaster_cls = requirementmaster_cls
            self.__userdata_cls = userdata_cls
        
        @property
        def config_cls(self):
            return self.__config_cls
        @property
        def prizemaster_cls(self):
            return self.__prizemaster_cls
        @property
        def requirementmaster_cls(self):
            return self.__requirementmaster_cls
        @property
        def userdata_cls(self):
            return self.__userdata_cls
    
    CONFIG = {
        Apps.KOIHIME : {
            'model' : ModelClsSet(PromotionConfigKoihime,
                               PromotionPrizeMasterKoihime,
                               PromotionRequirementMasterKoihime,
                               PromotionDataKoihime),
            'url' : dict(
                         release='http://10.116.41.10/khm/api/cro001',
                         staging='http://10.116.41.10/khm/api/cro001',
                         sandbox='http://10.116.41.10/khm/api/cro001'
                    ),
            'endpoint' : dict(
                        check = 'checkPromotion/Kyabaou/{userId}/{conditionId}',
                        conditionget = 'getCondition/Kyabaou/{conditionId}',
                    ),
        },
        Apps.CSC : {
            'model' : ModelClsSet(PromotionConfigCsc,
                               PromotionPrizeMasterCsc,
                               PromotionRequirementMasterCsc,
                               PromotionDataCsc),
            'url' : dict(
                         release='http://157.7.217.90/csc/sp',
                         staging='http://157.7.217.88/csc/sp',
                         sandbox='http://ec2-54-178-99-219.ap-northeast-1.compute.amazonaws.com/csc/sp'
                    ),
            'query' : dict(
                 release={OSAUtil.KEY_APP_ID:173706},
                 staging={OSAUtil.KEY_APP_ID:671226},
                 sandbox={OSAUtil.KEY_APP_ID:800520}
            ),
        },
        Apps.STANDARD : {
        },
    }
    DEFAULT_ENDPOINT = dict(
        check = 'promotioncheck/{appname}/{userId}/{conditionId}',
        conditionget = 'promotionconditionget/{appname}/{conditionId}',
    )

class PromotionUtil:
    
    @staticmethod
    def getPromotionConfigCls(appname):
        modelclsset = PromotionSettings.CONFIG.get(appname)
        return modelclsset['model'].config_cls if modelclsset else None
    
    @staticmethod
    def getPromotionPrizeMasterCls(appname):
        modelclsset = PromotionSettings.CONFIG.get(appname)
        return modelclsset['model'].prizemaster_cls if modelclsset else None
    
    @staticmethod
    def getPromotionRequirementMasterCls(appname):
        modelclsset = PromotionSettings.CONFIG.get(appname)
        return modelclsset['model'].requirementmaster_cls if modelclsset else None
    
    @staticmethod
    def getPromotionDataCls(appname):
        modelclsset = PromotionSettings.CONFIG.get(appname)
        return modelclsset['model'].userdata_cls if modelclsset else None
    
    @staticmethod
    def __makePromotionApiRequest(handler, appname, endpoint_key, endpoint_urlparams, sandbox, params, method='GET', post_json=True):
        conf = PromotionSettings.CONFIG.get(appname)
        if conf is None:
            return
        
        osa_util = handler.osa_util
        
        if settings_sub.CROSS_PROMOTION:
            urls = conf['url']
            conf_query = conf.get('query', {})
            
            if sandbox:
                environment_name = 'staging' if handler.html_param.get('is_staging') else 'sandbox'
            else:
                environment_name = 'release'
            url_head = urls[environment_name]
            queryparams = conf_query.get(environment_name) or {}
            
            endpoint_urlparams.update(appname='Kyabaou')
            endpoint_url_format = conf.get('endpoint', {}).get(endpoint_key, PromotionSettings.DEFAULT_ENDPOINT[endpoint_key])
            
            if queryparams:
                params = params or {}
                params.update(**queryparams)
        else:
            url_head = handler.url_cgi
            endpoint_urlparams.update(appname=appname)
            params = params or {}
            params[OSAUtil.KEY_APP_ID] = handler.appparam.app_id
            endpoint_url_format = PromotionSettings.DEFAULT_ENDPOINT[endpoint_key]
        
        endpoint_url = endpoint_url_format.format(**endpoint_urlparams)
        url = '%s/%s' % (url_head, endpoint_url)
        
        body = None
        if method.lower() == 'get':
            if params:
                for k,v in params.items():
                    url = OSAUtil.addQuery(url, k, urllib.quote(v, safe='') if isinstance(v, (str, unicode)) else v)
        else:
            body = ''
            if post_json:
                body = Json.encode(params or {})
            elif params:
                body = urllib.urlencode(params)
        
        handler.addlog(u'Promotion method:%s' % method)
        handler.addlog(u'Promotion url:%s' % url)
        
        headers = {}
        if osa_util.useragent.is_smartphone():
            # そのままユーザエージェントを送信.
            headers['User-Agent'] = osa_util.useragent.data
        else:
            # なんか適当につけとくか.
            headers['User-Agent'] = UserAgent.IOS_USERAGENT_SAMPLE
        
        def work(osa_util, url, body, http_method, headers):
            if settings_sub.IS_LOCAL:
                timeout = None
            else:
                timeout = 3
            if settings_sub.USE_LOG:
                handler.addlog('Promotion Headers:')
                for k,v in headers.items():
                    handler.addlog('　%s=%s' % (k,v))
            try:
                tmp = osa_util.httpopen(url, body, http_method, headers, timeout=timeout)
                response = tmp.read()
                return Json.decode(response)
            except urllib2.HTTPError, err:
                raise CabaretError(u'Promotion HTTPError:%s' % err)
            except Exception, err:
                raise CabaretError(u'PromotionError:%s' % err)
        return ThreadMethod(work, osa_util, url, body, method, headers)
    
    @staticmethod
    def requestPromotionAchieveFlags(handler, appname, dmmid, ridlist=None, do_execute=True):
        """プロモーション達成状態を問い合わせる.
        """
        sandbox = handler.appparam.sandbox
        
        if ridlist:
            conditionId = ','.join([str(rid) for rid in ridlist])
        else:
            conditionId = 'all'
        
        endpoint_urlparams = dict(
            userId = dmmid,
            conditionId = conditionId
        )
        requet = PromotionUtil.__makePromotionApiRequest(handler, appname, 'check', endpoint_urlparams, sandbox, None)
        reqkey = 'requestPromotionAchieveFlags:%s' % OSAUtil.makeSessionID()
        
        response = {}
        def cb(ret_data, reqkey, response):
            json_obj = ret_data[reqkey].get()
            for k,v in json_obj.items():
                if isinstance(v, (str, unicode)):
                    v = v.lower() in ('1', 'true')
                response[k] = v
        
        handler.addAppApiRequest(reqkey, requet, cb, reqkey, response)
        
        if do_execute:
            handler.execute_api()
        
        return response
    
    @staticmethod
    def requestPromotionConditionGet(handler, appname, ridlist=None, do_execute=True):
        """プロモーション達成条件を問い合わせる.
        """
        now = OSAUtil.get_now()
        namespace='PromotionCondition:%s' % appname
        
        sandbox = handler.appparam.sandbox
        
        not_found_ids = None
        
        cached_data = {}
        client = localcache.Client()
        if ridlist:
            cache_keys = [str(rid) for rid in ridlist]
            
            tmp = client.get_many(cache_keys, namespace=namespace)
            for k,v in tmp.items():
                if v['date'] < now:
                    continue
                cached_data[k] = v['data']
            
            not_found_ids = list(set(cache_keys) - set(cached_data.keys()))
            if not not_found_ids:
                return cached_data
        
        if not_found_ids:
            conditionId = ','.join(not_found_ids)
        else:
            conditionId = 'all'
        
        endpoint_urlparams = dict(
            conditionId = conditionId
        )
        requet = PromotionUtil.__makePromotionApiRequest(handler, appname, 'conditionget', endpoint_urlparams, sandbox, None)
        
        reqkey = 'requestPromotionConditionGet:%s' % OSAUtil.makeSessionID()
        
        response = cached_data
        def cb(ret_data, reqkey, response, client, cache_limitdate):
            json_obj = ret_data[reqkey].get()
            for k,v in json_obj.items():
                client.set(k, dict(data=v, date=cache_limitdate), namespace=namespace)
            response.update(json_obj)
        
        handler.addAppApiRequest(reqkey, requet, cb, reqkey, response, client, now + datetime.timedelta(seconds=3600*6))
        
        if do_execute:
            handler.execute_api()
        return response
    
    @staticmethod
    def chooseApplicationUrl(handler, config):
        """各環境別で設定されている相手側のURLを読み取る.
        """
        if handler.appparam.sandbox:
            if handler.html_param.get('is_staging'):
                postfix = '_stg'
            else:
                postfix = '_sandbox'
        else:
            postfix = ''
        return getattr(config, 'appurl_%s%s' % ('pc' if handler.is_pc else 'sp', postfix))
    
