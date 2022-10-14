# -*- coding: utf-8 -*-
import asyncio
import json
import logging
import os

import aiohttp

from pyapollo.constant import properties_config_file_format
from pyapollo.format_parser import DefaultContentParser
from pyapollo.parser_selector import get_format_parser


class AsyncApolloClient:
    def __init__(self, app_id, namespace_list=None, cluster='default', config_server_url='http://localhost:8080',
                 timeout=35, ip=None):
        self.config_server_url = config_server_url
        self.appId = app_id
        self.cluster = cluster
        self.timeout = timeout
        self.stopped = False
        self.init_ip(ip)

        self._stopping = False
        self._cache = {}
        if namespace_list and type(namespace_list) == list:
            self._notification_map = {namespace: -1 for namespace in namespace_list}
        else:
            self._notification_map = {'application': -1}

    def init_ip(self, ip):
        if ip:
            self.ip = ip
        else:
            import socket
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 53))
                ip = s.getsockname()[0]
            finally:
                s.close()
            self.ip = ip

    # Main method
    async def get_value(self, key, default_val=None, namespace='application', auto_fetch_on_cache_miss=False):
        (file_name, file_suffix) = os.path.splitext(namespace)
        if file_suffix == properties_config_file_format:
            namespace = file_name

        if namespace not in self._notification_map:
            self._notification_map[namespace] = -1
            logging.getLogger(__name__).info("Add namespace '%s' to local notification map", namespace)

        if namespace not in self._cache:
            self._cache[namespace] = {}
            logging.getLogger(__name__).info("Add namespace '%s' to local cache", namespace)
            # This is a new namespace, need to do a blocking fetch to populate the local cache
            await self._long_poll()

        if key in self._cache[namespace]:
            return self._cache[namespace][key]
        else:
            if auto_fetch_on_cache_miss:
                return await self._cached_http_get(key, default_val, namespace)
            else:
                return default_val

    async def start(self):
        if len(self._cache) == 0:
            await self._long_poll()

        await self._listener()

    async def load_config(self):
        if len(self._cache) == 0:
            await self._long_poll()
            logging.getLogger(__name__).info("namespace %s Loaded", self._notification_map)

        if len(self._cache) == 0:
            raise Exception("Load failed")

    def get_value_from_cache(self, key, default_val=None, namespace='application'):
        (file_name, file_suffix) = os.path.splitext(namespace)
        if file_suffix == properties_config_file_format:
            namespace = file_name

        if key in self._cache[namespace]:
            return self._cache[namespace][key]
        else:
            return default_val

    def stop(self):
        self._stopping = True
        logging.getLogger(__name__).info("Stopping listener...")

    async def _cached_http_get(self, key, default_val, namespace='application'):
        url = '{}/configfiles/json/{}/{}/{}?ip={}'.format(self.config_server_url, self.appId, self.cluster, namespace,
                                                          self.ip)
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(url=url, timeout=self.timeout) as response:
                if response.ok:
                    data = await response.json()
                    data = self._parse(namespace, data)
                    self._cache[namespace] = data
                    logging.getLogger(__name__).info('Updated local cache for namespace %s', namespace)
                else:
                    data = self._cache[namespace]

                if key in data:
                    return data[key]
                else:
                    return default_val

    async def _uncached_http_get(self, namespace='application'):
        url = '{}/configs/{}/{}/{}?ip={}'.format(self.config_server_url, self.appId, self.cluster, namespace, self.ip)
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(url=url, timeout=self.timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    release_key = data['releaseKey']
                    data = self._parse(namespace, data['configurations'])
                    self._cache[namespace] = data
                    logging.getLogger(__name__).info('Updated local cache for namespace %s release key %s: %s',
                                                     namespace, release_key,
                                                     repr(self._cache[namespace]))

    async def _long_poll(self):
        url = '{}/notifications/v2'.format(self.config_server_url)
        notifications = []
        for key in self._notification_map:
            notification_id = self._notification_map[key]
            notifications.append({
                'namespaceName': key,
                'notificationId': notification_id
            })

        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(url=url, params={
                'appId': self.appId,
                'cluster': self.cluster,
                'notifications': json.dumps(notifications, ensure_ascii=False)
            }, timeout=self.timeout) as response:

                logging.getLogger(__name__).debug('Long polling returns %d: url=%s', response.status, response.url)

                if response.status == 304:
                    # no change, loop
                    logging.getLogger(__name__).debug('No change, loop...')
                    return

                if response.status == 200:
                    data = await response.json()
                    for entry in data:
                        ns = entry['namespaceName']
                        nid = entry['notificationId']
                        logging.getLogger(__name__).info("%s has changes: notificationId=%d", ns, nid)
                        await self._uncached_http_get(ns)
                        self._notification_map[ns] = nid
                else:
                    logging.getLogger(__name__).warning('Sleep...')
                    await asyncio.sleep(self.timeout)

    async def _listener(self):
        logging.getLogger(__name__).info('Entering listener loop...')
        while not self._stopping:
            try:
                await self._long_poll()
            except asyncio.TimeoutError:
                logging.getLogger(__name__).warning('listener loop Timeout, Again!')

        logging.getLogger(__name__).info("Listener stopped!")
        self.stopped = True

    @staticmethod
    def _parse(namespace, content):
        parser: DefaultContentParser = get_format_parser(os.path.splitext(namespace)[-1])
        return parser.parse(content)
