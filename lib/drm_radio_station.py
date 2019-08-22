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


class DrmRadioStation(RadioStation):
    """
    Broadcast parameters for Digital Radio Mondiale (DRM) radio stations.
    """
    def __init__(self, name, sid):
        """
        @param name: The radio station name.

        @param sid: The broadcast service identifier (SId).
        """
        RadioStation.__init__(self, "drm", name)

        if re.match('^[0-9A-F]{6}$', sid, re.IGNORECASE):
            self._sid = sid
        else:
            raise ValueError("Invalid sid")

    def _get_query(self):
        return [self._sid]

class AmssRadioStation(RadioStation):
    """
    Broadcast parameters for AM Signaling System (AMSS) stations.
    """
    def __init__(self, name, sid):
        """
        @param name: The radio station name.

        @param sid: The broadcast service identifier (SId).
        """
        RadioStation.__init__(self, "amss", name)

        if re.match('^[0-9A-F]{6}$', sid, re.IGNORECASE):
            self._sid = sid
        else:
            raise ValueError("Invalid sid")

    def _get_query(self):
        return [self._sid]
