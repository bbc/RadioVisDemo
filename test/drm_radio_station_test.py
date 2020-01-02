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

"""
Test cases for DrmRadioStation and AmssRadioStation classes.
"""

from lib.drm_radio_station import DrmRadioStation, AmssRadioStation

def test_DrmRadioStation():
    p = DrmRadioStation('DRM Station', 'abcdef')
    assert p.get_hostname() == 'abcdef.drm.radiodns.org'
    assert p.get_text_topic() == '/topic/drm/abcdef/text'
    assert p.get_image_topic() == '/topic/drm/abcdef/image'
    assert p.get_name() == 'DRM Station'

def test_AmssRadioStation():
    p = AmssRadioStation('AMSS Station', 'abcdef')
    assert p.get_hostname() == 'abcdef.amss.radiodns.org'
    assert p.get_text_topic() == '/topic/amss/abcdef/text'
    assert p.get_image_topic() == '/topic/amss/abcdef/image'
    assert p.get_name() == 'AMSS Station'
