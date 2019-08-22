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

import dns.resolver
import logging
import socket


class ServiceRecord:
    def __init__(self,
                 name = None,
                 query = None,
                 port = None,
                 priority = None,
                 target = None,
                 weight = None):
        self.name = name
        self.query = query
        self.port = port
        self.priority = priority
        self.target = target
        self.weight = weight


class DnsResolver:
    """
    A simple wrapper for the dns.resolver.Resolver class.
    """
    def __init__(self):
        self._resolver = dns.resolver.get_default_resolver()

        # List of all host names (unqualified, fully-qualified, and IP
        # addresses) that refer to the local host (both loopback interface
        # and external interfaces). This is used for determining
        # preferred targets.
        self._localhost_names = [
            "localhost",
            "127.0.0.1",
            socket.gethostbyname(socket.gethostname()),
            socket.gethostname(),
            socket.getfqdn(socket.gethostname())
        ]

    def get_cname(self, host):
        """
        Return the CNAME (canonical name) for the given host.
        """
        cname = None

        if self.is_local(host):
            # Don't perform DNS lookup for localhost.
            cname = host
        else:
            self.log("Resolving host: " + host)

            try:
                ans = self._resolver.query(host, 'CNAME')

                if len(ans.rrset.items) == 1:
                    # Remove last (blank) field from host name.
                    labels = ans[0].target.labels[0:-1]
                    labels = map(lambda s: str(s, 'utf-8'), labels)
                    cname = '.'.join(labels)

            except dns.resolver.NoAnswer as e:
                self.log("No answer")
            except dns.resolver.NXDOMAIN as e:
                pass
            except dns.exception.DNSException as e:
                self.log("Exception: " + str(type(e)))

        return cname

    def get_services(self, srv_record, host_name, service_name):
        """
        Return a list of ServiceRecord objects for the DNS SRV records on the
        given host.
        """
        ans = None

        # Form service record query: _radiovis._tcp at example.com
        # becomes _radiovis._tcp.example.com
        query = '.'.join([srv_record, host_name])

        self.log("Querying: " + query)

        try:
            ans = self._resolver.query(query, 'SRV')

        except dns.resolver.NoAnswer as e:
            self.log("No answer")
        except dns.resolver.NXDOMAIN as e:
            pass
        except dns.exception.DNSException as e:
            self.log("Exception: " + str(type(e)))

        services = []

        if ans is not None and len(ans) > 0:
            for record in ans:
                # Remove last (blank) field from hostname then create
                # hostname string by joining with ".".
                target = record.target.labels[0:-1]
                target = map(lambda s: str(s, 'utf-8'), target)
                target = ".".join(target)

                self.log("Found: " + target + ", port " + str(record.port))

                service_record = ServiceRecord(name = service_name,
                                               query = query,
                                               port = record.port,
                                               priority = record.priority,
                                               target = target,
                                               weight = record.weight)
                services.append(service_record)
        else:
            self.log("No services")

        return services

    def is_local(self, host):
        return host in self._localhost_names

    def log(self, message):
        logging.info(message)
