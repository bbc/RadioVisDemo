# Copyright 2024 British Broadcasting Corporation
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

import re

import stomp


class RadioVisClient(stomp.ConnectionListener):
    def __init__(self,
                 host = 'localhost',
                 port = 61613,
                 proxy_settings = None,
                 user = None,
                 passcode = None):

        stomp.ConnectionListener.__init__(self)


        self._listeners = []

        self._connection = stomp.Connection10(host_and_ports = [(host, port)])
        self._connection.set_listener('', self)

        self._text_topic = None
        self._image_topic = None

        self._text_regex = re.compile(r"""
                                      ^TEXT   # "TEXT" at start of line
                                      \s+     # some whitespace
                                      (.*)    # the text message
                                      """,
                                      re.VERBOSE | re.IGNORECASE)

        self._show_regex = re.compile(r"""
                                      ^SHOW   # "SHOW" at start of line
                                      \s+     # some whitespace
                                      (.*)    # the URL of the image to show
                                      """,
                                      re.VERBOSE | re.IGNORECASE)

    def add_listener(self, listener):
        self._listeners.append(listener)

    def remove_listener(self, listener):
        self._listeners.remove(listener)

    def start(self, text_topic = None, image_topic = None):
        self._text_topic = text_topic
        self._image_topic = image_topic

        self._connection.connect(wait = True)

    def stop(self):
        self._connection.disconnect()
        self._connection.transport.stop()

    def on_connected(self, headers, body):
        """
        Once connected, subscribe to the message queues for TEXT and SHOW
        messages.
        """
        self.notify("CONNECTED", headers, body)

        if self._text_topic is not None:
            self._connection.subscribe(destination = self._text_topic, ack = 'auto')

        if self._image_topic is not None:
            self._connection.subscribe(destination = self._image_topic, ack = 'auto')

    def on_disconnected(self):
        self.notify("lost connection")

    def on_message(self, headers, body):
        """
        Handler for received MESSAGE frames. Parse the message body
        to extract TEXT and SHOW RadioVIS messages.
        """
        self.notify("MESSAGE", headers, body)

        lines = body.split('\n')

        for line in lines:
            # Remove leading and trailing whitespace.
            line = line.strip()

            # Check for TEXT message.
            match = self._text_regex.match(line)

            if match:
                # TODO: text should be no more than 128 characters.
                text = match.group(1)
                self.notify_text(text)
            else:
                # Check for SHOW message.
                match = self._show_regex.match(line)

                if match:
                    url = match.group(1)

                    if 'link' in headers:
                        link = headers['link']
                    else:
                        link = None

                    if 'trigger-time' in headers:
                        # TODO: Parse date_time and construct a datetime object.
                        date_time = headers['trigger-time']
                    else:
                        date_time = None

                    self.notify_show(url, link, date_time)
                else:
                    pass

    def on_receipt(self, headers, body):
        self.notify("RECEIPT", headers, body)

    def on_error(self, headers, body):
        """
        Handler for received ERROR frames.
        """
        self.notify("ERROR", headers, body)

    def disconnect(self, args):
        try:
            self._connection.disconnect()
        except stomp.NotConnectedException:
            pass # ignore if no longer connected

    def notify(self, message, headers = None, body = ''):
        for listener in self._listeners:
            listener.stomp_message(message)

            if headers is not None:
                for header in headers:
                    listener.stomp_message("%s: %s" % (header, headers[header]))

            if len(body) > 0:
                listener.stomp_message(body)

    def notify_text(self, text):
        """
        Notify listeners of a RadioVIS TEXT message.
        """
        for listener in self._listeners:
            listener.radiovis_text(text)

    def notify_show(self, url, link, date_time):
        """
        Notify listeners of a RadioVIS SHOW message.
        """
        for listener in self._listeners:
            listener.radiovis_show(url, link, date_time)

    def send_text_message(self, topic, text):
        """
        Send a TEXT RadioVIS message.
        """
        message = "TEXT " + text

        self._connection.send(destination = topic, message = message)

    def send_show_message(self, topic, image_url, link_url = None, date_time = None):
        """
        Send a SHOW RadioVIS message.
        """
        message = "SHOW " + image_url

        headers = {}

        if link_url is not None:
            headers['link'] = link_url

        if date_time is None:
            headers['trigger-time'] = 'NOW'
        else:
            headers['trigger-time'] = date_time

        self._connection.send(destination = topic, message = message, headers = headers)
