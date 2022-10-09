import logging
import os

import requests
from requests import ReadTimeout

from pyapollo import ApolloClient
from pyapollo.constant import properties_config_file_format
from pyapollo.format_parser import DefaultContentParser
from pyapollo.parser_selector import get_format_parser


class StrengthenApolloClient(ApolloClient):
    def __init__(self, app_id, namespace_list=None, *args, **kwargs):
        super().__init__(app_id, *args, **kwargs)
        if namespace_list:
            self._notification_map = {namespace: -1 for namespace in namespace_list}

    def get_value(self, key, default_val=None, namespace='application', auto_fetch_on_cache_miss=False):
        (file_name, file_suffix) = os.path.splitext(namespace)
        if file_suffix == properties_config_file_format:
            namespace = file_name

        return super().get_value(key, default_val, namespace, auto_fetch_on_cache_miss)

    def _listener(self):
        """
        _long_poll  调用 notifications/v2 接口 appid 的配置没有更新会一直block,
        如果 携带 timeout， 但未更新则 raise ReadTimeout，这会导致轮询监听配置中心的thread done,
        则不能对配置文件动态更新了，因此需要捕获

        """
        logging.getLogger(__name__).info('Entering listener loop...')
        while not self._stopping:
            try:
                self._long_poll()
            except ReadTimeout:
                logging.getLogger(__name__).warning('listener loop Timeout, Again!')

        logging.getLogger(__name__).info("Listener stopped!")
        self.stopped = True

    def _cached_http_get(self, key, default_val, namespace='application'):
        url = '{}/configfiles/json/{}/{}/{}?ip={}'.format(self.config_server_url, self.appId, self.cluster, namespace,
                                                          self.ip)
        r = requests.get(url)
        if r.ok:
            data = r.json()
            data = self._parse(namespace, data)
            self._cache[namespace] = data
            logging.getLogger(__name__).info('Updated local cache for namespace %s', namespace)
        else:
            data = self._cache[namespace]

        if key in data:
            return data[key]
        else:
            return default_val

    def _uncached_http_get(self, namespace='application'):
        url = '{}/configs/{}/{}/{}?ip={}'.format(self.config_server_url, self.appId, self.cluster, namespace, self.ip)
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            release_key = data['releaseKey']
            data = self._parse(namespace, data['configurations'])
            self._cache[namespace] = data
            logging.getLogger(__name__).info('Updated local cache for namespace %s release key %s: %s',
                                             namespace, release_key,
                                             repr(self._cache[namespace]))

    @staticmethod
    def _parse(namespace, content):
        parser: DefaultContentParser = get_format_parser(os.path.splitext(namespace)[-1])
        return parser.parse(content)
