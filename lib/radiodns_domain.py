# Copyright 2010 British Broadcasting Corporation
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

class RadioDnsDomainList(object):
    """
    A list of RadioDNS domains.
    """
    def __init__(self, filename):
        self._radiodns_domains = []

        tree = xml.etree.ElementTree.parse(filename)

        for domain in tree.findall("radiodns_domain"):
            self._radiodns_domains.append(domain.text)

        self._index = 0

    def next(self):
        """
        Return the next domain in the list.
        """
        if self._index >= len(self._radiodns_domains):
            self._index = 0
            raise StopIteration
        else:
            index = self._index
            self._index = index + 1
            return self._radiodns_domains[index]

    def __getitem__(self, index):
        return self._radiodns_domains[index]

    def __iter__(self):
        return self

    def __len__(self):
        return len(self._radiodns_domains)
