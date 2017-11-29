import urllib
import json

from defines import Defines


class DXPAPI:
    """connect to DXP API
    """
    error_code = Defines.DXP.ErrorCode

    def __init__(self, is_rel=False, is_R18=False):
        """initial method."""
        scheme = 'https'
        if Defines.DXP.ow_is_release and is_rel:
            subdomain = 'dxp'
        else:
            subdomain = 'sbx-dxp'
        if is_R18:
            domain = '{subdomain}.dmm.co.jp'.format(subdomain=subdomain)
        else:
            domain = '{subdomain}.dmm.com'.format(subdomain=subdomain)    
        self.api_uri = '{scheme}://{domain}/{url}'.format(
            scheme=scheme,
            domain=domain,
            url='{url}')

    def offerwall_url(self, app_id, user_id, device='sp'):
        """link to offerwall api."""
        params = {
            'app_id_from': self.urlquery_app_id_from(app_id),
            'user_id': self.urlquery_user_id(user_id),
            'device': self.urlquery_device(device),
        }
        uri = self.api_uri.format(
            url='offerwall?{app_id_from}&{user_id}&{device}').format(**params)
        return uri

    def set_wall_conversion(self, conversion_id):
        """wall conversion setting."""
        params = {
            'conversion_id': self.urlquery_conversion_id(conversion_id),
        }
        uri = self.api_uri.format(
            url='set_conversion?{conversion_id}').format(**params)

        res = self._connect_to_api(uri)
        if res['result'] == 'OK':
            is_configured = res['isConfigured']
        else:
            is_configured = None
        return is_configured

    def get_wall_conversion(self, app_id, user_id):
        """get wall conversion id."""
        params = {
            'app_id': self.urlquery_app_id(app_id),
            'user_id': self.urlquery_user_id(user_id),
        }
        uri = self.api_uri.format(
            url='get_conversion?{app_id}&{user_id}').format(**params)

        res = self._connect_to_api(uri)
        if res['result'] == 'OK':
            conversion_id = res['conversion_id']
        else:
            conversion_id = None
        return conversion_id

    def set_incentive(self, conversion_id):
        """set incentive."""
        params = {
            'conversion_id': self.urlquery_conversion_id(conversion_id),
        }
        uri = self.api_uri.format(
            url='set_incentive?{conversion_id}').format(**params)

        res = self._connect_to_api(uri)
        if res['result'] == 'OK':
            is_configured = True
        else:
            is_configured = None
        return is_configured

    def get_incentive(self, app_id, user_id, from_app_id=None):
        """get incentive."""
        params = {
            'app_id': self.urlquery_incentive_app_id(app_id),
            'user_id': self.urlquery_incentive_user_id(user_id),
        }
        if from_app_id is None:
            uri = self.api_uri(url='/get_incentive?{app_id}&{user_id}')
        else:
            params.update({'from_app_id': self.urlquery_from_app_id(from_app_id)})
            uri = self.api_uri(url='get_incentive?{app_id}&{user_id}&{from_app_id}')

        res = self._connect_to_api(uri)
        if res['result'] == 'OK':
            result = True
        else:
            if res['error']['error_code'] == self.error_code.incentive_acquired:
                raise
            result = False
        return result

    def _connect_to_api(self, uri):
        """connect to offerwall api with GET method."""
        try:
            res = urllib.urlopen(uri)
            d = json.load(res)
        except (urllib.URLError, ValueError):
            d = {'result': 'NG'}
        return d

    def urlquery_conversion_id(self, conversion_id):
        """create url query parameter for conversion_id."""
        return 'conversion_id={conversion_id}'.format(conversion_id=conversion_id)

    def urlquery_user_id(self, user_id):
        """create url query parameter for user_id."""
        return 'user_id={user_id}'.format(user_id=user_id)

    def urlquery_app_id(self, app_id):
        """create url query parameter for app_id."""
        return 'app_id={app_id}'.format(app_id=app_id)

    def urlquery_app_id_from(self, app_id):
        """create url query parameter for app_id."""
        return 'app_id_from={app_id}'.format(app_id=app_id)

    def urlquery_from_app_id(self, from_app_id):
        """create url query parameter for from_app_id."""
        return 'from_app_id_from={from_app_id}'.format(from_app_id=from_app_id)

    def urlquery_incentive_app_id(self, app_id):
        """create url query parameter for incentive_app_id."""
        return 'incentive_app_id={incentive_app_id}'.format(incentive_app_id=app_id)

    def urlquery_incentive_user_id(self, user_id):
        """create url query parameter for incentive_user_id."""
        return 'incentive_user_id={incentive_user_id}'.format(incentive_user_id=user_id)

    def urlquery_device(self, device):
        """create url query parameter for device."""
        return 'device={sp}'.format(sp=device)
