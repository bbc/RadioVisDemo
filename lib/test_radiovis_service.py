# Copyright 2019 British Broadcasting Corporation
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

import xml.etree.ElementTree


class TestRadioVisService(object):
    """
    Connection parameters for a RadioVIS service not accessible by RadioDNS
    lookup.
    """
    def __init__(self, name, hostname, port, text_topic, image_topic):
        """
        @param name: The name of the RadioVIS service.

        @param hostname: The hostname of the RadioVIS server.

        @param port: The port number of the RadioVIS service.

        @param text_topic: The topic name for text messages.

        @param image_topic: The topic name for slideshow images.
        """
        self._name = name
        self._hostname = hostname
        self._text_topic = text_topic
        self._image_topic = image_topic

        try:
            port = int(port)
        except (TypeError, ValueError):
            raise ValueError("invalid port")

        self._port = port

    def get_name(self):
        return self._name

    def get_hostname(self):
        return self._hostname

    def get_port(self):
        return self._port

    def get_text_topic(self):
        return self._text_topic

    def get_image_topic(self):
        return self._image_topic


class TestRadioVisServiceList(object):
    """
    A list of test RadioVIS services (L{TestRadioVisService} objects).
    """
    def __init__(self, filename):
        """
        Load the list of test RadioVIS services from a config XML file.
        """
        self._test_radiovis_services = []

        tree = xml.etree.ElementTree.parse(filename)

        for test_radiovis_service in tree.findall("test_radiovis_service"):
            name        = test_radiovis_service.findtext("name")
            hostname    = test_radiovis_service.findtext("hostname")
            port        = test_radiovis_service.findtext("port")
            text_topic  = test_radiovis_service.findtext("text_topic")
            image_topic = test_radiovis_service.findtext("image_topic")

            if text_topic is not None and len(text_topic) == 0:
                text_topic = None

            if image_topic is not None and len(image_topic) == 0:
                image_topic = None

            service = TestRadioVisService(name,
                                          hostname,
                                          port,
                                          text_topic,
                                          image_topic)

            self._test_radiovis_services.append(service)

        self._index = 0

    def __next__(self):
        """
        Return the next L{TestRadioVisService} object in the list.
        """
        if self._index >= len(self._test_radiovis_services):
            self._index = 0
            raise StopIteration
        else:
            index = self._index
            self._index = index + 1
            return self._test_radiovis_services[index]

    def __getitem__(self, index):
        return self._test_radiovis_services[index]

    def __iter__(self):
        return self

    def __len__(self):
        return len(self._test_radiovis_services)
