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

import re

from .radio_station import RadioStation


class HdRadioStation(RadioStation):
    """
    Broadcast parameters for HD Radio stations.
    """
    def __init__(self, name, tx, cc):
        """
        @param name: The radio station name.

        @param tx: The broadcast transmitter identifier.

        @param cc: The broadcast country code.
        """
        RadioStation.__init__(self, "hd", name)

        if re.match('^[0-9A-F]{5}$', tx, re.IGNORECASE):
            self._tx = tx
        else:
            raise ValueError("Invalid tx")

        if re.match('^[0-9A-F]{3}$', cc, re.IGNORECASE):
            self._cc = cc
        else:
            raise ValueError("Invalid cc")

    def _get_query(self):
        return [self._tx, self._cc]
