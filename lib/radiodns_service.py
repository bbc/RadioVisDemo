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

import xml.etree.ElementTree


class RadioDnsService(object):
    def __init__(self, name, record):
        """
        @param name: The service name, e.g. "RadioVIS"
        
        @param record: the SRV record, e.g. "_radiovis._tcp"
        """
        self._name = name
        self._record = record

    def get_name(self):
        return self._name

    def get_record(self):
        return self._record


class RadioDnsServiceList(object):
    """
    A list of RadioDNS services (L{RadioDnsService} objects).
    """
    def __init__(self, filename):
        self._radiodns_services = []

        tree = xml.etree.ElementTree.parse(filename)

        for service in tree.findall("service"):
            name   = service.findtext("name")
            record = service.findtext("record")

            radiodns_service = RadioDnsService(name, record)

            self._radiodns_services.append(radiodns_service)

        self._index = 0

    def next(self):
        """
        Return the next L{RadioDnsService} object in the list.
        """
        if self._index >= len(self._radiodns_services):
            self._index = 0
            raise StopIteration
        else:
            index = self._index
            self._index = index + 1
            return self._radiodns_services[index]

    def __getitem__(self, index):
        return self._radiodns_services[index]

    def __iter__(self):
        return self

    def __len__(self):
        return len(self._radiodns_services)
