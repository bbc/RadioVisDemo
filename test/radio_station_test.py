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

"""
Test cases for RadioStation class.
"""

from radio_station import RadioStation

class TestRadioStation(RadioStation):
    def __init__(self):
        RadioStation.__init__(self, 'test', 'Test')

    def _get_query(self):
        return []

def test_RadioStation():
    p = TestRadioStation()
    assert p.get_hostname() == 'test.radiodns.org'
    assert p.get_name() == 'Test'

def test_RadioStation_set_domain():
    p = TestRadioStation()
    p.set_domain('example.com')
    assert p.get_hostname() == 'test.example.com'
    assert p.get_name() == 'Test'
