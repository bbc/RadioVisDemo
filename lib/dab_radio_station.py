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

from radio_station import RadioStation
import re


class DabRadioStation(RadioStation):
    """
    Broadcast parameters for DAB Digital Radio stations.
    """
    def __init__(self, name, ecc, eid, sid, scids, appty = None, uatype = None, pa = None):
        """
        @param name: The radio station name.

        @param ecc: The broadcast extended country code (ECC).

        @param eid: The broadcast ensemble identifier (EId). 

        @param sid: The broadcast service identifier (SId).

        @param scids: The broadcast service component identifier within the
        service (SCIdS).

        @param appty: The broadcast X-PAD application type (AppTy), if the
        audio service is delivered as data via X-PAD.

        @param uatype: The broadcast user application type (UAType). If AppTy
        is specified, UAType must also be specified.
        
        @param pa: The broadcast packet address, which is mandatory if the
        audio service is delivered as data in an independent service component.
        """
        RadioStation.__init__(self, "dab", name)

        if re.match('^[0-9A-F]{3}$', ecc, re.IGNORECASE):
            self._ecc = ecc
        else:
            raise ValueError, "Invalid ecc"

        if re.match('^[0-9A-F]{4}$', eid, re.IGNORECASE):
            self._eid = eid
        else:
            raise ValueError, "Invalid eid"

        if re.match('^[0-9A-F]{4}$', sid, re.IGNORECASE) \
        or re.match('^[0-9A-F]{8}$', sid, re.IGNORECASE):
            self._sid = sid
        else:
            raise ValueError, "Invalid sid"

        if re.match('^[0-9A-F]{1}$', scids, re.IGNORECASE) \
        or re.match('^[0-9A-F]{3}$', scids, re.IGNORECASE):
            self._scids = scids
        else:
            raise ValueError, "Invalid scids"

        if appty is not None:
            if re.match('^[0-9A-F]{2}$', appty, re.IGNORECASE):
                self._appty_uatype = appty
            else:
                raise ValueError, "Invalid appty"

            if uatype is not None:
                if re.match('^[0-9A-F]{3}$', uatype, re.IGNORECASE):
                    self._appty_uatype += "-" + uatype
                else:
                    raise ValueError, "Invalid uatype"
            else:
                raise ValueError, "Both appty and uatype must be specified"
            
            if pa is not None:
                raise ValueError, "pa and appty-uatype are mutually exclusive"
        else:
            if uatype is not None:
                raise ValueError, "Both appty and uatype must be specified"
            
            self._appty_uatype = None

        if pa is not None:
            try:
                pa = int(pa)
            except (ValueError, TypeError):
                raise ValueError, "Invalid pa"
    
            if pa >= 0 and pa <= 1023:
                self._pa = pa
            else:
                raise ValueError, "Invalid pa"

            if appty is not None or uatype is not None:
                raise ValueError, "pa and appty-uatype are mutually exclusive"
        else:
            self._pa = None

    def _get_query(self):
        query = []

        if self._appty_uatype is not None:
            query.append(self._appty_uatype)
        elif self._pa is not None:
            query.append(str(self._pa))

        query.extend([self._scids, self._sid, self._eid, self._ecc])
        return query
