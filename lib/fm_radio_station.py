# Copyright 2009-2011 British Broadcasting Corporation
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

from radio_station import RadioStation
import re

class FmRadioStation(RadioStation):
    """
    Broadcast parameters for VHF/FM radio stations.
    """
    def __init__(self, name, ecc = None, country = None, pi = None, freq = None):
        """
        @param name: The radio station name.

        @param ecc: The broadcast RDS extended country code.

        @param country: An ISO country code, if a broadcast ECC is unavailable.

        @param pi: The broadcast programme identification (PI) code.

        @param freq: The frequency on which the service is received, in 0.01 MHz
        units, e.g, 98.8 MHz would be represented as 9880.
        """
        RadioStation.__init__(self, "fm", name)

        # Programme identification (PI) code is 4 hex digits.
        if pi is not None and re.match('^[0-9A-F]{4}$', pi, re.IGNORECASE):
            self._pi = pi
        else:
            raise ValueError, "Invalid pi"

        if country is not None:
            # Check for 2-letter ISO country code.
            if re.match('^[A-Z]{2}$', country, re.IGNORECASE):
                self._country = country
            else:
                raise ValueError, "Invalid country"

            if ecc is not None:
                raise ValueError, "country and ecc are mutually exclusive"
        elif ecc is not None:
            # Check for 2-hex-digit extended country code, and concatenate
            # with the first character of the RDS PI code.

            if re.match('^[0-9A-F]{2}$', ecc, re.IGNORECASE):
                self._country = self._pi[0] + ecc
            else:
                raise ValueError, "Invalid extended country code"

        try:
            freq = int(freq)
        except (ValueError, TypeError):
            raise ValueError, "Invalid freq"

        if freq >= 0 and freq <= 99999:
            self._freq = "%05u" % freq
        else:
            raise ValueError, "Invalid freq"

    def _get_query(self):
        return [self._freq, self._pi, self._country]
