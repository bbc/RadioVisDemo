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

class RadioStation(object):
    """
    Base class for radio station broadcast parameters.
    """
    def __init__(self, tx_system, name):
        """
        @param tx_system: The RadioDNS transmission system identifier,
        e.g., "fm", "dab", "drm", etc.

        @param name: The radio station name.
        """
        self._tx_system = tx_system
        self._name = name
        self._domain = "radiodns.org"

    def get_name(self):
        """
        Return the radio station name.
        """
        return self._name

    def set_domain(self, domain):
        self._domain = domain

    def get_hostname(self):
        """
        Return the fully-qualified domain name (FQDN) for the radio station.
        """
        query = self._get_query()
        query.extend([self._tx_system, self._domain])
        return ".".join(query)

    def get_text_topic(self):
        """
        Return the RadioVIS topic name for text messages.
        """
        return self._get_topic() + "/text"

    def get_image_topic(self):
        """
        Return the RadioVIS topic name for slideshow images.
        """
        return self._get_topic() + "/image"

    def _get_topic(self):
        # RadioVIS topic names are constructed from the same fields as RadioDNS
        # domain names, but in the reverse order. Example:
        # 0.c221.ce15.ce1.dab.radiodns.org -> /topic/dab/ce1/ce15/c221/0/text
        query = self._get_query()
        query.append(self._tx_system)
        query.reverse()
        return "/topic/" + "/".join(query)

    def _get_query(self):
        raise NotImplementedError("_get_query must be overridden in derived classes")
