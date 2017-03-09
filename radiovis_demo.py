#!/usr/bin/env python

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

"""
Entry point for the RadioVisDemo application.
"""

import logging
import os.path
import threading
import wx

from lib.main_frame import MainFrame
from lib.connection_manager import ConnectionManager
from lib.radio_station_list import RadioStationList
from lib.radiodns_domain import RadioDnsDomainList
from lib.radiodns_service import RadioDnsServiceList
from lib.test_radiovis_service import TestRadioVisServiceList


class RadioVisDemoApp(wx.App):
    """
    Application class.
    """
    def __init__(
        self, redirect = False, filename = None, useBestVisual = False,
        clearSigInt = True):

        # Directory for config files.
        self._config_dir = "conf"

        wx.App.__init__(self, redirect, filename, useBestVisual, clearSigInt)

    def OnInit(self):
        """
        Load data from the config files and create the main window.
        """

        radio_stations = RadioStationList(
            self._get_config_pathname("radio_stations.xml"))

        radiodns_domains = RadioDnsDomainList(
            self._get_config_pathname("radiodns_domains.xml"))

        radiodns_services = RadioDnsServiceList(
            self._get_config_pathname("radiodns_services.xml"))

        test_radiovis_services = TestRadioVisServiceList(
            self._get_config_pathname("test_radiovis_services.xml"))

        frame = MainFrame(parent = None,
                          id = wx.ID_ANY,
                          title = "RadioVIS Demo Application")

        self.SetTopWindow(frame)
        frame.Show()

        frame.set_radio_stations(radio_stations)
        frame.set_radiodns_domains(radiodns_domains)
        frame.set_test_radiovis_services(test_radiovis_services)

        connection_manager = ConnectionManager(radiodns_services)

        frame.set_connection_manager(connection_manager)
        return True

    def _get_config_pathname(self, filename):
        """
        Return the full pathname of for a given config file.
        """
        return os.path.join(self._config_dir, filename)

def init_logging():
    logger = logging.getLogger() # Get the root logger
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    logger.addHandler(stream_handler)


if __name__ == '__main__':
    thread = threading.currentThread()
    thread.setName("gui") # Allow the GUI thread to be identified.

    init_logging()

    app = RadioVisDemoApp()
    app.MainLoop()
