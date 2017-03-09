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

"""
Test cases for DabRadioStation class.
"""

from dab_radio_station import DabRadioStation

from nose.tools import assert_raises

def test_DabRadioStation():
    p = DabRadioStation(name = 'BBC Radio 1', ecc = 'ce1', eid = 'ce15', sid = 'c221', scids = '0')
    assert p.get_hostname() == '0.c221.ce15.ce1.dab.radiodns.org'
    assert p.get_text_topic() == '/topic/dab/ce1/ce15/c221/0/text'
    assert p.get_image_topic() == '/topic/dab/ce1/ce15/c221/0/image'
    assert p.get_name() == 'BBC Radio 1'

def test_DabRadioStation_pa():
    p = DabRadioStation(name = 'BBC Radio 1', ecc = 'abc', eid = 'abcd', sid = 'abcd', scids = '0', pa = 1023)
    assert p.get_hostname() == '1023.0.abcd.abcd.abc.dab.radiodns.org'
    assert p.get_text_topic() == '/topic/dab/abc/abcd/abcd/0/1023/text'
    assert p.get_image_topic() == '/topic/dab/abc/abcd/abcd/0/1023/image'
    assert p.get_name() == 'BBC Radio 1'

def test_DabRadioStation_appty_uatype():
    p = DabRadioStation(name = 'BBC Radio 1', ecc = 'abc', eid = 'abcd', sid = 'abcd', scids = '0', appty = '01', uatype = '234')
    assert p.get_hostname() == '01-234.0.abcd.abcd.abc.dab.radiodns.org'
    assert p.get_text_topic() == '/topic/dab/abc/abcd/abcd/0/01-234/text'
    assert p.get_image_topic() == '/topic/dab/abc/abcd/abcd/0/01-234/image'
    assert p.get_name() == 'BBC Radio 1'

def test_DabRadioStation_appty_uatype_missing_uatype():
    assert_raises(ValueError, DabRadioStation, name = 'BBC Radio 1', ecc = 'abc', eid = 'abcd', sid = 'abcd', scids = '0', appty = '01')

def test_DabRadioStation_appty_uatype_missing_appty():
    assert_raises(ValueError, DabRadioStation, name = 'BBC Radio 1', ecc = 'abc', eid = 'abcd', sid = 'abcd', scids = '0', uatype = '234')

def test_DabRadioStation_both_pa_and_appty_uatype():
    assert_raises(ValueError, DabRadioStation, name = 'BBC Radio 1', ecc = 'abc', eid = 'abcd', sid = 'abcd', scids = '0', pa = 1023, appty = '01', uatype = '234')
