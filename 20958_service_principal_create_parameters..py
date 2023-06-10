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


class ServicePrincipalCreateParameters(Model):
    """
    Request parameters for create a new service principal

    :param app_id: Gets or sets application Id
    :type app_id: str
    :param account_enabled: Specifies if the account is enabled
    :type account_enabled: bool
    """ 

    _validation = {
        'app_id': {'required': True},
        'account_enabled': {'required': True},
    }

    _attribute_map = {
        'app_id': {'key': 'appId', 'type': 'str'},
        'account_enabled': {'key': 'accountEnabled', 'type': 'bool'},
    }

    def __init__(self, app_id, account_enabled):
        self.app_id = app_id
        self.account_enabled = account_enabled
