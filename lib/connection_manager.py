# Copyright 2009 British Broadcasting Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License. You may
# obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.

import logging
import socks
import urllib
import urlparse

from async_http_client import HttpClientThread
from dns_resolver import DnsResolver
from proxy_settings import ProxySettings
from radiovis_client import RadioVisClient


class ConnectionManager(object):
    """
    Manages the RadioVIS (Stomp) connection and HTTP connection for retrieving
    images.
    """
    def __init__(self, radiodns_services):
        self._radiodns_services = radiodns_services
        self._dns = DnsResolver()

        self._proxy_settings = None
        self._use_http_proxy = False

        self._radiovis_client = None

        self._http_client = HttpClientThread(self)
        self._http_client.start()

        self._listeners = []

        # Get system proxy server settings (from http_proxy environment variable
        # or web browser settings).
        proxies = urllib.getproxies()
        if "http" in proxies:
            http_proxy = urlparse.urlparse(proxies['http'])
            self._proxy_settings = ProxySettings(proxy_type = socks.PROXY_TYPE_HTTP,
                                                 host = http_proxy.hostname,
                                                 port = http_proxy.port)

            self.log("HTTP proxy: " + http_proxy.hostname +
                     ", port " + str(http_proxy.port))
        else:
            self._proxy_settings = None
        
    def shutdown(self):
        if self._radiovis_client is not None:
            self._radiovis_client.stop()
            self._radiovis_client.remove_listener(self)

        self._http_client.stop()

    def add_listener(self, listener):
        self._listeners.append(listener)

    def remove_listener(self, listener):
        self._listeners.remove(listener)
        
    def get_cname(self, station):
        """
        Return the CNAME DNS record for the given radio station.
        """
        host = station.get_hostname()

        return self._dns.get_cname(host)

    def get_services(self, cname):
        """
        Return a list of the RadioDNS services available on the cname domain.
        Each entry in the list is a ServiceRecord object.
        """
        services = []

        for service in self._radiodns_services:
            dns_services = self._dns.get_services(service.get_record(),
                                                  cname,
                                                  service.get_name())

            services.extend(dns_services)

        return services

    def enable_http_proxy(self, enable):
        self._use_http_proxy = enable

    def connect_radiovis(self, host, port, station, use_proxy_server):
        """
        Establish a RadioVIS Stomp connection at the specified host and port,
        and optionally route the connection through the proxy server.
        """
        # Dispose of the old RadioVisClient object.
        if self._radiovis_client is not None:
            self._radiovis_client.stop()
            self._radiovis_client.remove_listener(self)
            self._radiovis_client = None

        if use_proxy_server:
            proxy_settings = self._proxy_settings
        else:
            proxy_settings = None

        self._radiovis_client = RadioVisClient(host, port, proxy_settings)

        self._radiovis_client.add_listener(self)
        self._radiovis_client.start(text_topic = station.get_text_topic(),
                                    image_topic = station.get_image_topic())

    def stomp_message(self, message):
        for listener in self._listeners:
            listener.stomp_message(message)

    def radiovis_text(self, text):
        """
        Called from RadioVisClient object when a TEXT message is received.
        """
        for listener in self._listeners:
            listener.radiovis_text(text)

    def radiovis_show(self, image_url, link_url, date_time):
        """
        Called from RadioVisClient object when a SHOW message is received.
        """
        for listener in self._listeners:
            listener.radiovis_show(image_url, link_url, date_time)

        if image_url is not None:
            self._request_image(image_url)

    def _request_image(self, url):
        proxy_settings = None

        if self._use_http_proxy:
            proxy_settings = self._proxy_settings

        self._http_client.request(url, proxy_settings)

    def http_received_data(self, data):
        """
        Called from HttpClientThread object when a file has been downloaded
        over HTTP.
        """
        if data is not None:
            for listener in self._listeners:
                listener.radiovis_image(data)

    def log(self, message):
        logging.info(message)
