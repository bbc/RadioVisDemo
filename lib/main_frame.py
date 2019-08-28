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

import io
import logging
import threading
import wx

from .dns_resolver import ServiceRecord


class RadioStationAdapter:
    def __init__(self, station):
        self._station = station

    def get_display_name(self):
        name     = self._station.get_name()
        hostname = self._station.get_hostname()

        display_name = "%s: %s" % (name, hostname)
        return display_name

    def get_hostname(self):
        return self._station.get_hostname()

    def resolve(self, connection_manager):
        cname = connection_manager.get_cname(self._station)
        services = []

        if cname is not None:
            services = connection_manager.get_services(cname)

        return (cname, services)

    def get_station(self):
        return self._station


class TestRadioVisServiceAdapter:
    def __init__(self, test_radiovis_service):
        self._test_radiovis_service = test_radiovis_service

    def get_display_name(self):
        name     = self._test_radiovis_service.get_name()
        hostname = self._test_radiovis_service.get_hostname()
        port     = self._test_radiovis_service.get_port()

        display_name = "%s: %s, port %d" % (name, hostname, port)
        return display_name

    def get_hostname(self):
        return self._test_radiovis_service.get_hostname()

    def resolve(self, connection_manager):
        cname = self._test_radiovis_service.get_hostname()
        port  = self._test_radiovis_service.get_port()

        service = ServiceRecord(name   = "RadioVIS",
                                target = cname,
                                port   = port)

        return (cname, [service])

    def get_station(self):
        return self._test_radiovis_service


class LogHandler(logging.Handler):
    """
    A custom logging hander class that passes log messages to
    the MainFrame object, for display in the GUI.
    """
    def __init__(self, dest):
        logging.Handler.__init__(self)

        self._dest = dest

        formatter = logging.Formatter("%(message)s")
        self.setFormatter(formatter)

    def emit(self, record):
        message = self.format(record)
        self._dest.log(message)


myEVT_LOG_MESSAGE = wx.NewEventType()
EVT_LOG_MESSAGE = wx.PyEventBinder(myEVT_LOG_MESSAGE, 1)

class LogMessageEvent(wx.PyCommandEvent):
    """
    Event to append a message to the message list.
    """
    def __init__(self, etype, eid, message):
        """
        Create the event object.
        """
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._message = message

    def get_message(self):
        """
        Return the message string from the event.
        """
        return self._message


myEVT_RADIOVIS_TEXT = wx.NewEventType()
EVT_RADIOVIS_TEXT = wx.PyEventBinder(myEVT_RADIOVIS_TEXT, 1)

class RadioVisTextEvent(wx.PyCommandEvent):
    """
    Event to append a text message to the text list.
    """
    def __init__(self, etype, eid, text):
        """
        Create the event object.
        """
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._text = text

    def get_text(self):
        """
        Return the text string from the event.
        """
        return self._text


myEVT_RADIOVIS_SHOW = wx.NewEventType()
EVT_RADIOVIS_SHOW = wx.PyEventBinder(myEVT_RADIOVIS_SHOW, 1)

class RadioVisShowEvent(wx.PyCommandEvent):
    """
    Event to append a text message to the text list.
    """
    def __init__(self, etype, eid, url, link, date_time):
        """
        Create the event object.
        """
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._url       = url
        self._link      = link
        self._date_time = date_time

    def get_image_url(self):
        """
        Return the image URL from the event.
        """
        return self._url

    def get_link_url(self):
        """
        Return the image hyperlink URL from the event.
        """
        return self._link


myEVT_RECEIVED_IMAGE = wx.NewEventType()
EVT_RECEIVED_IMAGE = wx.PyEventBinder(myEVT_RECEIVED_IMAGE, 1)

class ReceivedImageEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid, image_data):
        """
        Create the event object.
        """
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._image_data = image_data

    def get_image_data(self):
        """
        Return the raw image data from the event.
        """
        return self._image_data


class MainFrame(wx.Frame):
    """
    Application main window class.
    """
    def __init__(
        self, parent, id, title, pos = wx.DefaultPosition,
        size = wx.DefaultSize, style = wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self._connection_manager = None
        self._services = []

        self._init_logging()

        self._default_width = 400

        panel = wx.Panel(parent = self,
                         id = wx.ID_ANY)

        # hgap is amount of space between columns, vgap between rows
        column1_sizer = wx.FlexGridSizer(cols = 2, hgap = 10, vgap = 5)
        column1_sizer.AddGrowableCol(1)

        column2_sizer = wx.FlexGridSizer(cols = 2, hgap = 10, vgap = 5)
        column2_sizer.AddGrowableCol(1)

        self._init_domain_controls(panel, column1_sizer)
        self._init_hostname_controls(panel, column1_sizer)
        self._init_cname_controls(panel, column1_sizer)
        self._init_services_controls(panel, column1_sizer)
        self._init_connect_controls(panel, column1_sizer)
        self._init_log_controls(panel, column1_sizer)
        self._init_messages_controls(panel, column1_sizer)
        self._init_image_url_controls(panel, column1_sizer)
        self._init_link_url_controls(panel, column1_sizer)

        self._init_image_controls(panel, column2_sizer)
        self._init_text_controls(panel, column2_sizer)

        self._init_close_button(panel)

        content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        content_sizer.Add(column1_sizer, proportion = 1, flag = wx.ALL | wx.EXPAND, border = 10)
        content_sizer.Add(column2_sizer, proportion = 1, flag = wx.ALL | wx.EXPAND, border = 10)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer(1)
        button_sizer.Add(self._close_button,
                         proportion = 0,
                         flag = wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND,
                         border = 10)

        # Use a BoxSizer to add a border/gap around sizer.
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(content_sizer, proportion = 1, flag = wx.EXPAND)
        border.Add(button_sizer, proportion = 0, flag = wx.EXPAND)
        panel.SetSizerAndFit(border)
        self.Fit()

        self._init_message_handlers()

    def _init_domain_controls(self, parent, sizer):
        self._domain_static = wx.StaticText(parent = parent,
                                              id = wx.ID_ANY,
                                              label = "Domain")

        self._domain_combobox = wx.ComboBox(parent = parent,
                                            size = (self._default_width, -1),
                                            style = wx.CB_READONLY)

        sizer.Add(self._domain_static)
        sizer.Add(self._domain_combobox, flag = wx.EXPAND)

        self._domain_combobox.Append("radiodns.org")
        self._domain_combobox.SetSelection(0)

    def _init_hostname_controls(self, parent, sizer):
        self._hostname_static = wx.StaticText(parent = parent,
                                              id = wx.ID_ANY,
                                              label = "Hostname")

        self._hostname_combobox = wx.ComboBox(parent = parent,
                                              size = (self._default_width, -1),
                                              style = wx.CB_READONLY)

        sizer.Add(self._hostname_static)
        sizer.Add(self._hostname_combobox, flag = wx.EXPAND)

        resolve_button = wx.Button(parent = parent,
                                   id = wx.ID_ANY,
                                   label = "Resolve")

        self.Bind(wx.EVT_BUTTON, self.OnResolveButton, resolve_button)

        sizer.AddSpacer(0)
        sizer.Add(resolve_button)

    def _init_cname_controls(self, parent, sizer):
        self._cname_static = wx.StaticText(parent = parent,
                                           id = wx.ID_ANY,
                                           label = "CNAME")

        self._cname_text = wx.TextCtrl(parent = parent,
                                       id = wx.ID_ANY,
                                       size = (self._default_width, -1),
                                       style = wx.TE_READONLY)

        sizer.Add(self._cname_static)
        sizer.Add(self._cname_text, flag = wx.EXPAND)

    def _init_services_controls(self, parent, sizer):
        self._services_static = wx.StaticText(parent = parent,
                                              id = wx.ID_ANY,
                                              label = "Services")

        self._services_listctrl = wx.ListCtrl(parent,
                                              wx.ID_ANY,
                                              style = wx.LC_REPORT | wx.SUNKEN_BORDER)

        self._services_listctrl.InsertColumn(0, "Name", wx.LIST_FORMAT_LEFT, 70)
        self._services_listctrl.InsertColumn(1, "Port", wx.LIST_FORMAT_LEFT, 50)
        self._services_listctrl.InsertColumn(2, "Priority", wx.LIST_FORMAT_LEFT, 50)
        self._services_listctrl.InsertColumn(3, "Weight", wx.LIST_FORMAT_LEFT, 50)
        self._services_listctrl.InsertColumn(4, "Target", wx.LIST_FORMAT_LEFT, 140)

        sizer.Add(self._services_static)
        sizer.Add(self._services_listctrl, flag = wx.EXPAND)

    def _init_log_controls(self, parent, sizer):
        self._log_static = wx.StaticText(parent = parent,
                                         id = wx.ID_ANY,
                                         label = "Log")

        self._log_listbox = wx.ListBox(parent = parent,
                                       id = wx.ID_ANY,
                                       size = (self._default_width, 100))

        sizer.Add(self._log_static)
        sizer.Add(self._log_listbox, flag = wx.EXPAND)

        self._set_current_row_growable(sizer)

    def _init_messages_controls(self, parent, sizer):
        self._messages_static = wx.StaticText(parent = parent,
                                              id = wx.ID_ANY,
                                              label = "Messages")

        self._messages_listbox = wx.ListBox(parent = parent,
                                            id = wx.ID_ANY,
                                            size = (self._default_width, 100))

        sizer.Add(self._messages_static)
        sizer.Add(self._messages_listbox, flag = wx.EXPAND)

        self._set_current_row_growable(sizer)

    def _init_connect_controls(self, parent, sizer):
        connect_button = wx.Button(parent = parent,
                                   id = wx.ID_ANY,
                                   label = "Connect")

        self.Bind(wx.EVT_BUTTON, self.OnConnectButton, connect_button)

        self._proxy_http_button = wx.CheckBox(parent = parent,
                                              id = wx.ID_ANY,
                                              label = "Use proxy server for HTTP connection")

        self._proxy_stomp_button = wx.CheckBox(parent = parent,
                                               id = wx.ID_ANY,
                                               label = "Use proxy server for Stomp connection")

        self._proxy_stomp_button.Disable()

        connect_sizer = wx.BoxSizer(wx.HORIZONTAL)
        connect_sizer.Add(connect_button, flag = wx.ALIGN_TOP)
        connect_sizer.AddSpacer(10)

        checkbox_sizer = wx.GridSizer(cols = 1, vgap = 4, hgap = 0)
        checkbox_sizer.Add(self._proxy_http_button)
        checkbox_sizer.Add(self._proxy_stomp_button)

        connect_sizer.Add(checkbox_sizer, flag = wx.ALIGN_CENTER_VERTICAL)

        sizer.AddSpacer(0)
        sizer.Add(connect_sizer)

    def _init_image_url_controls(self, parent, sizer):
        self._image_url_static = wx.StaticText(parent = parent,
                                               id = wx.ID_ANY,
                                               label = "Image URL")

        self._image_url_text = wx.TextCtrl(parent = parent,
                                           id = wx.ID_ANY,
                                           size = (self._default_width, -1),
                                           style = wx.TE_READONLY)

        sizer.Add(self._image_url_static)
        sizer.Add(self._image_url_text, flag = wx.EXPAND)

    def _init_link_url_controls(self, parent, sizer):
        self._link_url_static = wx.StaticText(parent = parent,
                                              id = wx.ID_ANY,
                                              label = "Link URL")

        self._link_url_text = wx.TextCtrl(parent = parent,
                                          id = wx.ID_ANY,
                                          size = (self._default_width, -1),
                                          style = wx.TE_READONLY)

        sizer.Add(self._link_url_static)
        sizer.Add(self._link_url_text, flag = wx.EXPAND)

    def _init_image_controls(self, parent, sizer):
        self._image_static = wx.StaticText(parent = parent,
                                           id = wx.ID_ANY,
                                           label = "Image")

        # TODO: the +4 here is to allow for the sunken border (2 pixels on each side).
        self._image_static_bitmap = wx.StaticBitmap(parent = parent,
                                                    id = wx.ID_ANY,
                                                    size = (320 + 4, 240 + 4),
                                                    style = wx.ST_NO_AUTORESIZE | wx.BORDER_SUNKEN)

        sizer.Add(self._image_static)
        sizer.Add(self._image_static_bitmap)

    def _init_text_controls(self, parent, sizer):
        self._text_static = wx.StaticText(parent = parent,
                                          id = wx.ID_ANY,
                                          label = "Text")

        self._text_text = wx.TextCtrl(parent = parent,
                                      id = wx.ID_ANY,
                                      size = (self._default_width, -1),
                                      style = wx.TE_READONLY | wx.TE_MULTILINE)

        color_white = wx.Colour(255, 255, 255)
        color_blue  = wx.Colour(0, 0, 128)

        self._image_static_bitmap.SetBackgroundColour(color_white)

        font = wx.Font(pointSize = 14,
                       family = wx.FONTFAMILY_SWISS,
                       style = wx.FONTSTYLE_NORMAL,
                       weight = wx.FONTWEIGHT_NORMAL,
                       underline = False,
                       faceName = "Verdana",
                       encoding = wx.FONTENCODING_SYSTEM)

        self._text_text.SetFont(font)
        self._text_text.SetForegroundColour(color_blue)
        self._text_text.SetBackgroundColour(color_white)

        sizer.Add(self._text_static)
        sizer.Add(self._text_text, flag = wx.EXPAND)

        self._set_current_row_growable(sizer)

    def _init_close_button(self, parent):
        self._close_button = wx.Button(parent = parent,
                                       id = wx.ID_ANY,
                                       label = "Close")

        self.Bind(wx.EVT_BUTTON, self.OnCloseButton, self._close_button)

    def _init_message_handlers(self):
        self.Bind(EVT_LOG_MESSAGE, self.OnLogMessage)
        self.Bind(EVT_RADIOVIS_TEXT, self.OnRadioVisText)
        self.Bind(EVT_RADIOVIS_SHOW, self.OnRadioVisShow)
        self.Bind(EVT_RECEIVED_IMAGE, self.OnReceivedImage)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self._domain_combobox.Bind(wx.EVT_COMBOBOX, self.OnDomainComboBoxSelChanged)

    def _set_current_row_growable(self, sizer):
        """
        Set the current row in a wx.FlexGridSizer object as growable.
        """
        rows, cols = sizer.CalcRowsCols()
        sizer.AddGrowableRow(rows - 1)

    def set_radio_stations(self, radio_stations):
        self._radio_stations = radio_stations

        for station in radio_stations:
            item = RadioStationAdapter(station)
            self._hostname_combobox.Append(item.get_display_name(), item)

        if self._hostname_combobox.GetCount() > 0:
            self._hostname_combobox.SetSelection(0)

    def set_radiodns_domains(self, radiodns_domains):
        self._domain_combobox.Clear()

        for domain in radiodns_domains:
          self._domain_combobox.Append(domain)

        if self._domain_combobox.GetCount() > 0:
            self._domain_combobox.SetSelection(0)

        self._update_hostnames()

    def set_test_radiovis_services(self, test_radiovis_services):
        for test_radiovis_service in test_radiovis_services:
            item = TestRadioVisServiceAdapter(test_radiovis_service)
            self._hostname_combobox.Append(item.get_display_name(), item)

        if self._hostname_combobox.GetCount() > 0:
            self._hostname_combobox.SetSelection(0)

    def set_connection_manager(self, connection_manager):
        self._connection_manager = connection_manager
        self._connection_manager.add_listener(self)

    def OnResolveButton(self, event):
        """
        Event handler for the "Resolve" button.
        """
        self._cname_text.SetValue("")
        self._services_listctrl.DeleteAllItems()

        index = self._hostname_combobox.GetSelection()
        item = self._hostname_combobox.GetClientData(index)

        cname, self._services = item.resolve(self._connection_manager)

        if cname is not None:
            self._cname_text.SetValue(cname)

            self._append_log("CNAME: " + cname)
        else:
            self._append_log("Unknown hostname: " + item.get_hostname())

        for i in range(len(self._services)):
            service = self._services[i]
            idx = self._services_listctrl.InsertItem(0, service.name)
            self._services_listctrl.SetItem(idx, 1, str(service.port))
            self._services_listctrl.SetItem(idx, 2, str(service.priority))
            self._services_listctrl.SetItem(idx, 3, str(service.weight))
            self._services_listctrl.SetItem(idx, 4, service.target)
            self._services_listctrl.SetItemData(idx, i)

        if self._services_listctrl.GetItemCount() > 0:
            self._services_listctrl.SetItemState(0, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

    def OnDomainComboBoxSelChanged(self, event):
        self._update_hostnames()

    def _update_hostnames(self):
        sel = self._hostname_combobox.GetSelection()
        self._hostname_combobox.Clear()

        domain = self._domain_combobox.GetValue()

        for station in self._radio_stations:
            station.set_domain(domain)
            item = RadioStationAdapter(station)
            self._hostname_combobox.Append(item.get_display_name(), item)

        if sel != wx.NOT_FOUND:
            self._hostname_combobox.SetSelection(sel)

    def OnCloseButton(self, event):
        """
        Event handler for the "Close" button.
        """
        self.Close(True)

    def OnConnectButton(self, event):
        """
        Event handler for the "Connect" button.
        """
        host_index = self._hostname_combobox.GetSelection()
        item = self._hostname_combobox.GetClientData(host_index)
        station = item.get_station()

        selected_item = self._services_listctrl.GetFirstSelected();
        service = None

        if selected_item != -1:
            index = self._services_listctrl.GetItemData(selected_item)
            service = self._services[index]

        proxy_http  = self._proxy_http_button.IsChecked()
        proxy_stomp = self._proxy_stomp_button.IsChecked()

        if service is not None and host_index != wx.NOT_FOUND:
            if service.name == "RadioVIS":
                # Reset Image URL, Link URL, and Text fields when connecting to a new service
                self._image_url_text.SetValue("")
                self._link_url_text.SetValue("")
                self._text_text.SetValue("")
                self._image_static_bitmap.SetBitmap(wx.NullBitmap)

                # Connect.
                self._append_log("Connect to: " + service.target)

                target  = service.target
                port    = service.port

                self._connection_manager.enable_http_proxy(proxy_http)
                self._connection_manager.connect_radiovis(target, port, station, proxy_stomp)
            else:
                self._message_box("Please select a RadioVIS service to connect to")
        else:
            if len(self._services) > 0:
                self._message_box("Please select an entry in the Services list")
            else:
                self._message_box("This radio station has no services available")

    def OnClose(self, event):
        """
        Handler for the wx.EVT_CLOSE event.
        """
        self._connection_manager.shutdown()
        self._connection_manager.remove_listener(self)
        self.Destroy()

    def log(self, message):
        """
        If called on the main GUI thread, we can add items to the listbox
        control directly. If called on another thread, post a message to the GUI
        thread to add the item.
        """
        if threading.currentThread().getName() == 'gui':
            self._append_log(message)
        else:
            self._post_log_message(message)

    def stomp_message(self, message):
        """
        This function is called in the context of the stomp worker thread,
        so post a message to the GUI thread.
        """
        self._post_log_message(message)

    def _post_log_message(self, message):
        evt = LogMessageEvent(myEVT_LOG_MESSAGE, -1, message)
        wx.PostEvent(self, evt)

    def OnLogMessage(self, evt):
        """
        Handler for the EVT_LOG_MESSAGE event.
        """
        self._append_log(evt.get_message())

    def radiovis_text(self, text):
        """
        This function is called in the context of the stomp worker thread,
        so post a message to the GUI thread.
        """
        evt = RadioVisTextEvent(myEVT_RADIOVIS_TEXT, -1, text)
        wx.PostEvent(self, evt)

    def OnRadioVisText(self, evt):
        """
        Handler for the EVT_RADIOVIS_TEXT event.
        """
        text = evt.get_text()
        self._append_message(text)
        self._text_text.SetValue(text)

    def radiovis_show(self, url, link, date_time):
        evt = RadioVisShowEvent(myEVT_RADIOVIS_SHOW, -1, url, link, date_time)
        wx.PostEvent(self, evt)

    def OnRadioVisShow(self, evt):
        """
        Handler for the EVT_RADIOVIS_SHOW event.
        """
        image_url = evt.get_image_url()
        link_url  = evt.get_link_url()

        if link_url is not None:
            self._link_url_text.SetValue(link_url)

        if image_url is not None:
            self._image_url_text.SetValue(image_url)

    def radiovis_image(self, image_data):
        evt = ReceivedImageEvent(myEVT_RECEIVED_IMAGE, -1, image_data)
        wx.PostEvent(self, evt)

    def OnReceivedImage(self, event):
        """
        Handler for the EVT_RECEIVED_IMAGE event.
        """
        image_data = event.get_image_data()

        bitmap = self.create_bitmap(image_data)

        if bitmap is not None:
            self._image_static_bitmap.SetBitmap(bitmap)

    def create_bitmap(self, image_data):
        """
        Create and return a wx.Bitmap object from image data, which may be
        PNG, JPG, GIF, or other format.
        """
        stream = io.BytesIO(image_data)

        bitmap = None

        try:
            image = wx.Image(stream)
            bitmap = wx.Bitmap(image)
        except wx.wxAssertionError as ex:
            # Invalid image data.
            logging.warning("Couldn't create image")

        return bitmap

    def _init_logging(self):
        """
        Configure the logging module to output messages to a LogHandler object,
        which passes the messages to MainFrame.log(), for display in the GUI.
        """
        logger = logging.getLogger() # Get the root logger

        log_handler = LogHandler(self)
        log_handler.setLevel(logging.INFO)
        logger.addHandler(log_handler)

    def _append_log(self, message):
        """
        Append a string to the "Log" listbox.
        """
        index = self._log_listbox.Append(message)
        self._log_listbox.SetSelection(index)

    def _append_message(self, message):
        """
        Append a string to the "Messages" listbox.
        """
        index = self._messages_listbox.Append(message)
        self._messages_listbox.SetSelection(index)

    def _message_box(self, message):
        """
        Display a popup message box.
        """
        return wx.MessageBox(message, self.GetTitle())
