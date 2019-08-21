# RadioVIS Demo Application v1.0

## Introduction

RadioVISDemo is a demonstration application for RadioDNS and RadioVIS. RadioVIS
is the visualisation protocol that forms part of the RadioDNS suite of
application protocols. The software follows RadioDNS Technical Specification
v0.6 and RadioVIS Technical Specification V1.0.0.

Please visit <http://radiodns.org> for more information about RadioDNS, and
<http://www.bbc.co.uk/rd/projects/radiovis> to obtain the latest release of this
software.

## Installation

RadioVISDemo is a Python application and requires several software to be
installed.

On Windows, download install the following packages:

 * Python v2.5 or later: <http://www.python.org/download/>

 * wxPython v4.0 or later: <http://www.wxpython.org>

 * dnspython v1.6.0 or later: <http://www.dnspython.org>

 * setuptools v0.6c9 or later: <http://pypi.python.org/pypi/setuptools>

 * nose v1.0.0: <https://nose.readthedocs.org>

On Linux systems, use your package manager to install the following packages:

 * python
 * wxPython (or python-wxgtk3.0)
 * python-dns
 * python-setuptools
 * python-nose

On Mac, you can use PIP to install the following packages:

 * `pip install wxPython`
 * `pip install dnspython`
 * `pip install nose` 


### Ubuntu

    $ sudo apt-get install python-wxgtk3.0 python-dnspython python-nose 


RadioVisDemo was developed on Windows using the
[ActiveState](http://www.activestate.com) Python distribution,
and has been tested on Windows XP and Ubuntu v8.10.

The source code includes a modified version of Jason R Briggs's stomp.py module,
which implements the STOMP protocol. Please visit
<https://code.google.com/p/stomppy/> for more information.

# Running RadioVISDemo

To run the application, enter the following at a command prompt:

    python radiovis_demo.py

The default setting in the **Domain** field is "radiodns.org". Change this option
to perform radio station DNS lookups against a different domain, which is useful
for testing RadioDNS services during development.

Select a RadioDNS hostname in the **Hostname** field. The **Local Stomp Server** entry
allows testing of a RadioVIS service running on the local machine (localhost,
port 61613).

Press the **Resolve** button to perform a DNS CNAME lookup on the selected hostname
and then an SRV record query for available RadioDNS services (RadioVIS, RadioTAG,
and RadioEPG). The results are shown in the **CNAME** and **Services** fields.

If a RadioVIS service is available, select this from the **Services** list and press
the **Connect** button. The options next to the **Connect** button allow HTTP requests
and the Stomp connection to be routed through an HTTP proxy. Proxy settings are
obtained from the `urllib.getproxies()` method, which returns the system proxy
settings (the `http_proxy` environment variable or Internet Explorer settings in
Windows). A proxy server should not be used if connecting to a service on the
local machine.

Once connected, the following fields show information received from the RadioVIS
service:

 * The **Log** field shows status messages and details of all Stomp messages
   received.

 * The **Messages** field shows the history of received RadioVIS TEXT messages.

 * The **Image URL** field shows the URL of the image from the last received
   RadioVIS SHOW message.

 * The **Link URL** field shows the hyperlink from the last received RadioVIS SHOW
   message.

 * The **Image** field shows the image from the last received RadioVIS SHOW message.

 * The **Text** field displays the last received RadioVIS TEXT message.

## Configuration

The RadioVIS demo application uses several configuration files, in the `conf`
directory:

### radiodns_domains.xml

This file contains a list of domains against which DNS lookups
for radio stations can be performed. By default, this list includes
radiodns.org and prototype0.net (which is a BBC development server),
but you can modify this list to refer to your own domain in order to test
your own RadioDNS services before making them available via radiodns.org.

### radio_stations.xml

This file contains a list of radio stations and their associated
broadcast parameters, which are shown in the **Hostname** field. Please read
the [RadioDNS documentation](http://radiodns.org/) for details of the
broadcast parameters.

### radiodns_services.xml

This file contains a list of the RadioDNS services and SRV
record names, which are queried when the **Resolve** button is pressed. At
present these are RadioVIS, RadioTAG, and RadioEPG.

### test_radiovis_services.xml

This file contains a list of test RadioVIS services that
the application can connect to. Each `test_radiovis_service` element should
contain the following entries:

 * `name`: The name of the test service name, for display in the user interface.

 * `hostname`: The hostname of the computer that runs the RadioVIS Stomp
   service.

 * `port`: The port number of the RadioVIS Stomp service.

 * `text_topic`: The topic name for text message notifications.

 * `image_topic`: The topic name for slideshow image notifications.

## Tests

The `test` directory contains unit tests. To run the tests use the following
command:

    nosetests

## Limitations

This software has a few limitations:

 * The software uses the system proxy server settings (the `http_proxy`
   environment variable or Internet Explorer settings in Windows), and these
   are not configurable within the program.

 * In the handling of RadioVIS SHOW messages, the trigger time is not used,
   and the image is always shown immediately.

 * Error and redirect statuses are not handled when retrieving images over HTTP.

## Resources

For more information, please visit BBC R&D's
[RadioVIS project page](http://www.bbc.co.uk/rd/projects/radiovis)
and the [RadioDNS website](http://radiodns.org/).

## Authors

This software was written by [Chris Needham](https://github.com/chrisn) - chris.needham at bbc.co.uk.

## Contact and Legal Information

Copyright 2009-2017 British Broadcasting Corporation

The RadioVIS Demo Application is free software; you can redistribute it and/or
modify it under the terms of the Apache License, Version 2.0.

The RadioVIS Demo Application is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.  See the Apache License, Version 2.0 for
more details.

Your comments and suggestions are welcome. Please visit our website at
http://www.bbc.co.uk/rd/projects/radiovis or send email to irfs@bbc.co.uk.
