# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft and contributors.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class DhcpOptions(Model):
    """
    DHCPOptions contains an array of DNS servers available to VMs deployed in
    the virtual networkStandard DHCP option for a subnet overrides VNET DHCP
    options.

    :param dns_servers: Gets or sets list of DNS servers IP addresses
    :type dns_servers: list of str
    """ 

    _attribute_map = {
        'dns_servers': {'key': 'dnsServers', 'type': '[str]'},
    }

    def __init__(self, dns_servers=None):
        self.dns_servers = dns_servers
