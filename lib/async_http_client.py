# Copyright 2020 British Broadcasting Corporation
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

import asyncore
import logging
import queue
import socket
import threading
import urllib


class AsyncHttpClient(asyncore.dispatcher_with_send):
    def __init__(self, client):
        asyncore.dispatcher_with_send.__init__(self)

        self._proxy_settings = None
        self._client = client
        self._data = None
        self._header = None
        self._request_host = None
        self._request_path = None

    def request(self, url, proxy_settings = None):
        self.log("Requesting URL: " + url)
        self._proxy_settings = proxy_settings

        if self._proxy_settings is None:
            url_components = urllib.parse.urlparse(url)
            self._request_host = url_components.hostname
            self._request_path = url_components.path
            self._request_port = url_components.port

            if self._request_port is None:
                self._request_port = 80
        else:
            self._request_host = None
            self._request_path = url

        self._header = None
        self._data = b""

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

        if self._proxy_settings is not None:
            host = self._proxy_settings.get_proxy_host()
            port = self._proxy_settings.get_proxy_port()
            self.log("Using proxy %s port %d" % (host, port))
            host_and_port = (host, port)
        else:
            host_and_port = (self._request_host, self._request_port)

        try:
            self.connect(host_and_port)
            result = True
        except socket.error as ex:
            self.log("Error %d connecting to %s port %d: %s" % (ex.errno, host_and_port[0], host_and_port[1], ex.strerror))
            result = False

        return result

    def handle_connect(self):
        request = "GET %s HTTP/1.1\r\n" % self._request_path

        if self._request_host is not None:
            request += "Host: %s" % self._request_host

            if self._request_port != 80:
                request += ":%d" % self._request_port

            request += "\r\n"

        request += "User-Agent: RadioVISDemo\r\n"
        request += "Accept: */*\r\n"
        request += "Connection: close\r\n"
        request += "\r\n"

        self.send(request.encode("utf-8"))

    def handle_expt(self):
        # connection failed
        self.close()
        self._client.http_closed()

    def handle_close(self):
        self.close()

        self._client.http_received_data(self._data)

        self._header = None
        self._data = b""

    def handle_read(self):
        data = self.recv(2048)

        if not self._header:
            # check if we have a full header
            self._data += data

            i = self._data.find(b"\r\n\r\n")

            if i == -1:
                return # no empty line
            else:
                self._header = self._data[:i + 2]
                data = self._data[i + 4:]
                self._data = b""

        if data:
            self._data += data

    def poll(self):
        asyncore.poll(0.2)

    def log(self, message):
        logging.info(message)


class HttpClientThread(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self._client = client
        self._queue = queue.Queue()
        self._http_client = None

    def request(self, url, proxy_settings = None):
        """
        Request a URL to be downloaded.
        """
        self._queue.put((url, proxy_settings))

    def run(self):
        while True:
            if self._http_client is not None:
                # Currently downloading a url,
                self._http_client.poll()

                # Check the queue to see if any urls have been posted
                try:
                    url, proxy_settings = self._queue.get_nowait()

                    if url is None:
                        self._queue.task_done()
                        break
                    else:
                        self.log("Discarding url: %s" % url)
                        self._queue.task_done()
                except queue.Empty:
                    pass
            else:
                # Wait for an item to appear in the queue.
                url, proxy_settings = self._queue.get()

                # If url is None, this is the signal to exit the thread.
                if url is None:
                    self._queue.task_done()
                    break

                self._request_url(url, proxy_settings)

    def stop(self):
        # Queueing a request where the url is None notifies the worker thread
        # to exit.
        self.request(None)
        self.join()

    def _request_url(self, url, proxy_settings):
        self._http_client = AsyncHttpClient(self)
        success = self._http_client.request(url, proxy_settings)

        if not success:
            self._done()

    def _done(self):
        self._queue.task_done()
        self._http_client = None

    def http_received_data(self, data):
        self._client.http_received_data(data)
        self._done()

    def http_closed(self):
        self._done()

    def log(self, message):
        logging.info(message)
