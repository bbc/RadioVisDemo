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

from dab_radio_station import DabRadioStation
from fm_radio_station import FmRadioStation
from hd_radio_station import HdRadioStation
from drm_radio_station import DrmRadioStation, AmssRadioStation


class RadioStationList(object):
    """
    A list of radio stations (L{RadioStation}-derived objects).
    """
    def __init__(self, filename):
    
        self._radio_stations = []

        tree = xml.etree.ElementTree.parse(filename)

        for element in tree.findall("radio_station"):
            radio_station = self._create_radio_station(element)

            if radio_station is not None:
                self._radio_stations.append(radio_station)

        self._index = 0

    def _create_radio_station(self, element):
        broadcast_protocol = element.findtext("broadcast_protocol")
        name = element.findtext("name")

        if broadcast_protocol == "fm":
            ecc     = element.findtext("ecc")
            country = element.findtext("country")
            pi      = element.findtext("pi")
            freq    = element.findtext("freq")

            radio_station = FmRadioStation(name, ecc, country, pi, freq)
        elif broadcast_protocol == "dab":
            ecc    = element.findtext("ecc")
            eid    = element.findtext("eid")
            sid    = element.findtext("sid")
            scids  = element.findtext("scids")
            appty  = element.findtext("appty")
            uatype = element.findtext("uatype")
            pa     = element.findtext("pa")

            radio_station = DabRadioStation(name, ecc, eid, sid, scids, appty, uatype, pa)
        elif broadcast_protocol == "drm":
            sid = element.findtext("sid")

            radio_station = DrmRadioStation(name, sid)
        elif broadcast_protocol == "amss":
            sid = element.findtext("sid")

            radio_station = AmssRadioStation(name, sid)
        elif broadcast_protocol == "hd":
            tx = element.findtext("tx")
            cc = element.findtext("cc")

            radio_station = HdRadioStation(name, tx, cc)
        else:
            raise ValueError, "Unknown broadcast protocol: %s" % broadcast_protocol

        return radio_station

    def next(self):
        """
        Return the next L{RadioStation} object in the list.
        """
        if self._index >= len(self._radio_stations):
            self._index = 0
            raise StopIteration
        else:
            index = self._index
            self._index = index + 1
            return self._radio_stations[index]

    def __getitem__(self, index):
        return self._radio_stations[index]

    def __iter__(self):
        return self

    def __len__(self):
        return len(self._radio_stations)


def main():
    radio_station_list = RadioStationList("radio_stations.xml")

    print "Loaded %d stations" % len(radio_station_list)

    for radio_station in radio_station_list:
        print radio_station

if __name__ == "__main__":
    main()
