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
Test cases for RadioStationList class.
"""

from lib.dab_radio_station import DabRadioStation
from lib.fm_radio_station import FmRadioStation
from lib.hd_radio_station import HdRadioStation
from lib.drm_radio_station import DrmRadioStation, AmssRadioStation
from lib.radio_station_list import RadioStationList

import io
import nose.tools

def test_RadioStationList():
    xml = """
    <radio_stations>
        <radio_station>
            <name>Test FM Station</name>
            <broadcast_protocol>fm</broadcast_protocol>
            <ecc>bc</ecc>
            <pi>abcd</pi>
            <freq>12345</freq>
        </radio_station>

        <radio_station>
            <name>BBC Radio 1</name>
            <broadcast_protocol>dab</broadcast_protocol>
            <ecc>ce1</ecc>
            <eid>ce15</eid>
            <sid>c221</sid>
            <scids>0</scids>
        </radio_station>

        <radio_station>
            <name>Test DRM Station</name>
            <broadcast_protocol>drm</broadcast_protocol>
            <sid>abcdef</sid>
        </radio_station>

        <radio_station>
            <name>Test AMSS Station</name>
            <broadcast_protocol>amss</broadcast_protocol>
            <sid>abcdef</sid>
        </radio_station>

        <radio_station>
            <name>Test HD Radio Station</name>
            <broadcast_protocol>hd</broadcast_protocol>
            <tx>aaaaa</tx>
            <cc>ccc</cc>
        </radio_station>
    </radio_stations>
    """

    stream = io.StringIO(xml)
    radio_stations = RadioStationList(stream)

    assert len(radio_stations) == 5
    assert isinstance(radio_stations[0], FmRadioStation)
    assert radio_stations[0].get_name() == "Test FM Station"
    assert radio_stations[0].get_hostname() == "12345.abcd.abc.fm.radiodns.org"

    assert isinstance(radio_stations[1], DabRadioStation)
    assert radio_stations[1].get_name() == "BBC Radio 1"
    assert radio_stations[1].get_hostname() == "0.c221.ce15.ce1.dab.radiodns.org"

    assert isinstance(radio_stations[2], DrmRadioStation)
    assert radio_stations[2].get_name() == "Test DRM Station"
    assert radio_stations[2].get_hostname() == "abcdef.drm.radiodns.org"

    assert isinstance(radio_stations[3], AmssRadioStation)
    assert radio_stations[3].get_name() == "Test AMSS Station"
    assert radio_stations[3].get_hostname() == "abcdef.amss.radiodns.org"

    assert isinstance(radio_stations[4], HdRadioStation)
    assert radio_stations[4].get_name() == "Test HD Radio Station"
    assert radio_stations[4].get_hostname() == "aaaaa.ccc.hd.radiodns.org"

def test_RadioStationList_Error():
    xml = """
    <radio_stations>
        <radio_station>
            <name>Test FM Station</name>
            <broadcast_protocol>unknown</broadcast_protocol>
        </radio_station>
    </radio_stations>
    """

    stream = io.StringIO(xml)

    nose.tools.assert_raises(ValueError, RadioStationList, stream)
