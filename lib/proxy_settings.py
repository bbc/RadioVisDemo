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

class ProxySettings(object):
    def __init__(self, proxy_type = None, host = None, port = None):
        self._type = proxy_type
        self._host = host
        self._port = port

    def get_proxy_type(self):
        return self._type

    def get_proxy_host(self):
        return self._host

    def get_proxy_port(self):
        return self._port
