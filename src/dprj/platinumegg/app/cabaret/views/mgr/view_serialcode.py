# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.SerialCampaign import SerialCampaignMaster,\
    SerialCode, ShareSerialLog
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import datetime
from platinumegg.app.cabaret.models.Player import PlayerConsumePoint
import urllib

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Handler(AdminHandler):
    """シリアルコード確認.
    シリアルコードの情報
        シリアルコードで検索
        ユーザで検索
        マスターIDで検索
        マスター毎の入力された数.
    """
    def process(self):
        model_mgr = self.getModelMgr()
        
        # HTMLのテーブル関係.
        self.__table_name = None
        self.__table_titles = None
        self.__table_data = []
        
        # 検索条件の初期値.
        self.html_param['_serchtype'] = ''
        self.html_param['_value'] = ''
        self.html_param['_mid'] = 0
        self.html_param['_date'] = OSAUtil.get_now().strftime("%Y-%m-%d")
        
        # 実行するプロセス.
        method = self.request.get('_proc')
        if method:
            func = getattr(self, '_proc_%s' % method, None)
            if func:
                func()
        self.html_param['table_name'] = self.__table_name
        self.html_param['table_titles'] = self.__table_titles
        self.html_param['table_data'] = self.__table_data
        
        # マスターデータ.
        serialcampaign_list = model_mgr.get_mastermodel_all(SerialCampaignMaster, 'id', using=backup_db)
        self.html_param['serialcampaign_list'] = serialcampaign_list
        
        # このページのURL.
        self.html_param['url_self'] = self.makeAppLinkUrl(self.__make_url_self())
        
        self.writeAppHtml('infomations/view_serialcode')
    
    def __make_url_self(self, **params):
        """HTML表示用のテーブルを初期化.
        """
        url = UrlMaker.view_serialcode()
        for k,v in params.items():
            url = OSAUtil.addQuery(url, k, v)
        return url
    
    def __init_table(self, table_name):
        """HTML表示用のテーブルを初期化.
        """
        self.__table_name = table_name
        self.__table_titles = []
        self.__table_data = []
    
    def __add_table_title(self, key, name):
        """HTML表示用のテーブルのタイトルを追加.
        """
        self.__table_titles.append((key, name))
    
    def __make_table_celldata(self, value, linkurl=None):
        """HTML表示用のテーブルのセル情報を作成.
        """
        return {
            'value' : value,
            'url' : linkurl,
        }
    
    def __add_table_data(self, data):
        """HTML表示用のテーブルのデータを追加.
        """
        if not isinstance(data, dict):
            raise CabaretError(u'テーブルのデータがdictではありません')
        self.__table_data.append(data)
    
    def _proc_view_record(self):
        """シリアルコードのレコード情報を表示.
        """
        CONTENT_NUM_PER_PAGE = 100
        # ページング.
        page = int(self.request.get('_page') or 0)
        
        # 検索条件を取得.
        serchtype = self.request.get('_serchtype')
        
        # 検索する日付.
        str_target_date = self.request.get('_date')
        
        # 検索用の値を取得.
        value = self.request.get('_value') or ''
        mid = self.request.get('_mid') or ''
        shareserial = self.request.get('_share') == '1'
        
        int_value = None
        if value.isdigit():
            int_value = int(value)
        self.html_param['_serchtype'] = serchtype
        self.html_param['_date'] = str_target_date
        self.html_param['_value'] = value
        self.html_param['_mid'] = mid
        self.html_param['shareserial'] = shareserial
        
        # シリアルコードの検索条件.
        filters = None
        if serchtype == 'uid':
            if int_value:
                filters = {
                    'uid' : int_value,
                }
        elif serchtype == 'dmmid':
            if value:
                uid = BackendApi.dmmid_to_appuid(self, [value], using=backup_db).get(value)
                if uid:
                    filters = {
                        'uid' : uid,
                    }
        elif serchtype == 'serial':
            if value:
                arr = list(set(value.split(',')))
                filters = {
                    'serial__in' : arr,
                }
        elif serchtype == 'mid':
            target_date = None
            if str_target_date:
                try:
                    target_date = DateTimeUtil.strToDateTime(str_target_date, "%Y-%m-%d")
                except:
                    pass
            if target_date is None:
                self.putAlertToHtmlParam(u'日付はyyyy-mm-ddで入力してください', AlertCode.ERROR)
                return
            
            if mid and mid.isdigit():
                mid = int(mid)
                master = BackendApi.get_serialcampaign_master(self.getModelMgr(), mid, using=backup_db)
                if master and master.share_serial == shareserial:
                    filters = {
                        'mid' : mid,
                        'itime__gte' : target_date,
                        'itime__lt' : target_date + datetime.timedelta(days=1),
                    }
        
        # シリアルコードを取得.
        serialcode_list = None
        has_next = False
        if filters:
            offset = page * CONTENT_NUM_PER_PAGE
            limit = CONTENT_NUM_PER_PAGE + 1
            model_cls = ShareSerialLog if shareserial else SerialCode
            serialcode_list = model_cls.fetchValues(filters=filters, order_by='-itime', limit=limit, offset=offset, using=backup_db)
            has_next = CONTENT_NUM_PER_PAGE < len(serialcode_list)
            serialcode_list = serialcode_list[:CONTENT_NUM_PER_PAGE]
        
        # 見つからなかった.
        if not serialcode_list:
            self.putAlertToHtmlParam(u'シリアルコードが見つかりませんでした', AlertCode.WARNING)
            return
        
        # テーブルのタイトル.
        self.__init_table(u'シリアルコード情報')
        self.__add_table_title('mid', u'キャンペーンID')
        self.__add_table_title('user', u'ユーザ')
        self.__add_table_title('serial', u'シリアルコード')
        self.__add_table_title('itime', u'入力した時間')
        self.__add_table_title('point', u'生涯課金額')
        self.__add_table_title('paymentlog', u'入力後2ヶ月間の購入履歴')
        
        # テーブルの作成.
        uidlist = list(set([serialcode.uid for serialcode in serialcode_list if 0 < serialcode.uid]))
        playerpoint_dict = dict([(model.id, model.point_total) for model in PlayerConsumePoint.getByKey(uidlist, using=backup_db)])
        url_paymentlog = OSAUtil.addQuery(UrlMaker.view_paymentlog(), '_logtype', 'gacha')
        url_paymentlog = OSAUtil.addQuery(url_paymentlog, '_is_complete', '1')
        url_paymentlog = OSAUtil.addQuery(url_paymentlog, '_serchtype', 'uid')
        
        for serialcode in serialcode_list:
            if serialcode.uid:
                url = UrlMaker.view_player(serialcode.uid)
                celldata_user = self.__make_table_celldata(serialcode.uid, self.makeAppLinkUrl(url))
                
                stime = serialcode.itime
                etime = serialcode.itime + datetime.timedelta(days=60)
                url = OSAUtil.addQuery(url_paymentlog, '_value', serialcode.uid)
                url = OSAUtil.addQuery(url, '_stime', urllib.quote(stime.strftime('%Y/%m/%d %H:%M:%S'), ''))
                url = OSAUtil.addQuery(url, '_etime', urllib.quote(etime.strftime('%Y/%m/%d %H:%M:%S'), ''))
                celldata_paymentlog = self.__make_table_celldata(u'購入履歴≫', self.makeAppLinkUrl(url))
            else:
                celldata_user = self.__make_table_celldata(u'未入力')
                celldata_paymentlog = self.__make_table_celldata(u'----')
            
            row = {
                'mid' : self.__make_table_celldata(serialcode.mid),
                'user' : celldata_user,
                'serial' : self.__make_table_celldata(serialcode.serial),
                'itime' : self.__make_table_celldata(serialcode.itime.strftime("%Y/%m/%d %H:%M:%S")),
                'point' : self.__make_table_celldata(playerpoint_dict.get(serialcode.uid, 0)),
                'paymentlog' : celldata_paymentlog,
            }
            self.__add_table_data(row)
        
        # ページング.
        url_prev = None
        url_next = None
        page_query_params = {
            '_proc' : 'view_record',
            '_serchtype' : serchtype,
            '_value' : value,
        }
        if 0 < page:
            url_prev = self.__make_url_self(_page=page-1, **page_query_params)
        if has_next:
            url_next = self.__make_url_self(_page=page+1, **page_query_params)
        self.html_param['url_prev'] = url_prev
        self.html_param['url_next'] = url_next
    
    def _proc_view_count(self):
        """シリアルコードの入力数を表示.
        """
        str_mid = self.request.get('_mid') or ''
        mid = None
        if str_mid.isdigit():
            mid = int(str_mid)
        self.html_param['_mid'] = str_mid
        
        # マスターデータ.
        model_mgr = self.getModelMgr()
        master = None
        if mid:
            master = BackendApi.get_serialcampaign_master(model_mgr, mid, using=backup_db)
        if master is None:
            self.putAlertToHtmlParam(u'存在しないシリアルコードキャンペーンです', AlertCode.ERROR)
            return
        
        # SQLを実行.
        if master.share_serial:
            query_set = ShareSerialLog.sql("WHERE `mid`=:1 group by DATE_FORMAT(itime,'%%Y/%%m/%%d'),is_pc", mid)
        else:
            query_set = SerialCode.sql("WHERE `mid`=:1 and `uid`>0 group by DATE_FORMAT(itime,'%%Y/%%m/%%d'),is_pc", mid)
        result = query_set.fetch("DATE_FORMAT(itime,'%%Y/%%m/%%d'),is_pc,count(*)", limit=None)
        if not result:
            self.putAlertToHtmlParam(u'入力数が見つかりませんでした', AlertCode.WARNING)
            return
        
        # 取得したデータを纏める.
        fixeddata = {}
        for str_date, is_pc, num in result:
            data = fixeddata[str_date] = fixeddata.get(str_date, {})
            data['pc' if is_pc else 'sp'] = int(num)
        
        # テーブルのタイトル.
        self.__init_table(u'シリアルコード入力数')
        self.__add_table_title('date', u'日付')
        self.__add_table_title('sp_num', u'入力数(SP)')
        self.__add_table_title('pc_num', u'入力数(PC)')
        
        # テーブルのデータ.
        keys = fixeddata.keys()
        keys.sort(reverse=True)
        for key in keys:
            data = fixeddata[key]
            row = {
                'date' : self.__make_table_celldata(key),
                'sp_num' : self.__make_table_celldata(data.get('sp', 0)),
                'pc_num' : self.__make_table_celldata(data.get('pc', 0)),
            }
            self.__add_table_data(row)

def main(request):
    return Handler.run(request)
