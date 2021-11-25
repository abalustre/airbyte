#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import re
import os
import json
import numbers
import certifi
import requests
import pandas as pd


from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteCatalog, AirbyteMessage, ConfiguredAirbyteCatalog, SyncMode, AirbyteMessage, AirbyteRecordMessage, Type
from datetime import datetime, timedelta
from io import StringIO
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


class GraphqlRequest(HttpStream):
    url_base = ""
    cursor_field = ""
    primary_key = ""

    def __init__(self, url: str, http_method: str, headers: Optional[str], body: Optional[str], json_source: Optional[str], json_field: Optional[str]):
        super().__init__()
        self.url_base = url
        self._http_method = http_method
        self._headers = headers
        self._body = body
        self._json_source = json_source
        self._json_field = json_field

    @property
    def http_method(self) -> str:
        return self._http_method

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        if self._headers:
            return self._headers

        return {}

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        if self._body:
            return self._body
        return None

    def _make_request(self):
        http_method = self._http_method.lower()
        url = self.url_base
        headers = self._headers
        body = self._body
        
        if http_method == "get":
            r = requests.get(url, headers=headers, json=body)
        elif http_method == "post":
            r = requests.post(url, headers=headers, json=body)
        else:
            raise Exception(f"Did not recognize http_method: {http_method}")

        return r

    def get_json_schema(self):
        schema = super().get_json_schema()

        resp = self._make_request()
        if resp.status_code == 200:
            root = json.loads(resp.content)
            if self._json_source == "root":
                df = pd.DataFrame.from_dict(root)
            else:
                field_list = self._json_field.split('.')
                
                for field in field_list:
                    if field == 'root':
                        for key in root.keys(): field = key   
                        root = root.get(field)
                    else:
                        root = root.get(field)

                df = pd.DataFrame.from_dict(root)
            headers = df.columns.tolist()

        properties = {}
        for header in headers:
            _type = "string"
            try:
                if isinstance(df.loc[0, header], numbers.Number):
                    _type = "number"
                elif isinstance(df.loc[0, header], dict):
                    _type = "object"

                parse(df.loc[0, header])
                _type = "date"
            except:
                pass

            properties[header] = {"description": "", "type": _type}

        new_schema = schema
        new_schema["required"] = []
        new_schema["properties"] = properties

        return new_schema
    
    def _has_next_page(self, input_dict={}):
        endCursor = ''
        if isinstance(input_dict, dict) and 'pageInfo' in input_dict.keys():
            if 'hasNextPage' in input_dict['pageInfo'].keys() and 'endCursor' in input_dict['pageInfo'].keys():
                if input_dict['pageInfo']['hasNextPage'] == True:
                    endCursor = input_dict['pageInfo']['endCursor']

        return endCursor
    
    def _get_next_page(self, endCursor=''):
        http_method = self._http_method.lower()
        url = self.url_base
        headers = self._headers
        body = self._body
        root = {}
        if len(endCursor) > 0:
            if 'after' in body['variables'].keys():
                body['variables']['after'] = endCursor
                if http_method == "get":
                    r = requests.get(url, headers=headers, json=body)
                elif http_method == "post":
                    r = requests.post(url, headers=headers, json=body)
                else:
                    raise Exception(f"Did not recognize http_method: {http_method}")
                
                if r.status_code == 200:
                    root = json.loads(r.content)

                    field_list = self._json_field.split('.')               
                    for field in field_list:
                        if field == "root":
                            for key in root.keys(): field = key   
                            root = root.get(field)
                        else:
                            endCursor = self._has_next_page(root)
                            root = root.get(field)
                    
                    root = list(filter(None.__ne__, root))#filter to remove none elements from the list

        return root, endCursor


    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        root = json.loads(response.content)
        if 'errors' not in root.keys():
            if self._json_source == "root":
                endCursor = self._has_next_page(root)
                
                yield from root

                while True:
                    root, endCursor = self._get_next_page(endCursor)
                    yield from root

                    if endCursor == '': break

            else:
                field_list = self._json_field.split('.')             
                for field in field_list:
                    if field == "root":
                        for key in root.keys(): field = key   
                        root = root.get(field)
                    else:
                        endCursor = self._has_next_page(root)
                        root = root.get(field)
                
                yield from root

                while True:
                    root, endCursor = self._get_next_page(endCursor)
                    yield from root

                    if endCursor == '': break
        else:
            raise Exception(f"{root}")
                          
class  SourceGraphqlRequest(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            resp = self._make_request(config, logger)
            status = resp.status_code
            logger.info(f"Ping response code: {status}")
            if status == 200:
                return True, None

            error = resp.json().get("error")
            code = error.get("code")
            message = error.get("message") or error.get("info")

            return False, message
        except Exception as e:
            return False, e
    
    def _get_host(self, url=''):
        try:
            if re.search('https://', url) != None:
                _end = re.search('https://', url).end()
                host = url[_end:].strip('/')
                if re.search(r'/..*', host):
                    _start = re.search(r'/..*', host).start()
                    host = host[:_start]
                return host
            else:
                _end = re.search('http://', url).end()
                host = url[_end:].strip('/')
                if re.search(r'/..*', host):
                    _start = re.search(r'/..*', host).start()
                    host = host[:_start]
                return host
        except Exception as e:
            raise e
    
    def _set_certify_ssl(self, host):
        try:
            os.environ['CERTIFI_PATH'] = certifi.where()
            cmd = "echo "" | openssl s_client -showcerts -connect " + host + ":443 2>/dev/null 2>/dev/null | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' >> $CERTIFI_PATH"
            os.system(cmd)
        except Exception as e:
            raise e
    
    def _is_valid_date(self, value):
        if value == "current":
            return True
        elif len(value.split(" ")) == 3:
            _value = value.replace("current ", "")
            if "-" in _value and _value.replace("- ", "").isdigit():
                return True
            elif "+" in _value and _value.replace("+ ", "").isdigit():
                return True
        return False

    def _get_value(self, value, unit):
        if self._is_valid_date(value):
            if value == "current":
                return datetime.today()
            elif "-" in value:
                digit = int(value.replace("current - ", ""))
                if unit == "day":
                    return datetime.today() - timedelta(days = digit)
                if unit == "month":
                    return datetime.today() - relativedelta(months = digit)
                if unit == "year":
                    return datetime.today() - relativedelta(years = digit)
            elif "+" in value:
                digit = int(value.replace("current + ", ""))
                if unit == "day":
                    return datetime.today() + timedelta(days = digit)
                if unit == "month":
                    return datetime.today() + relativedelta(months = digit)
                if unit == "year":
                    return datetime.today() + relativedelta(years = digit)

        raise Exception("Params malformed")

    def _make_request(self, config, logger):
        parsed_config = self._parse_config(config)
        http_method = parsed_config.get("http_method").lower()
        url = parsed_config.get("url")
        headers = parsed_config.get("headers", {})
        body = parsed_config.get("body", {})
        
        if http_method == "get":
            try:
                r = requests.get(url, headers=headers, json=body)
            except requests.exceptions.SSLError:
                _host = self._get_host(url)
                self._set_certify_ssl(_host)
                r = requests.get(url, headers=headers, json=body)
        elif http_method == "post":
            try:
                r = requests.post(url, headers=headers, json=body)
            except requests.exceptions.SSLError:
                _host = self._get_host(url)
                self._set_certify_ssl(_host)
                r = requests.post(url, headers=headers, json=body)
        else:
            raise Exception(f"Did not recognize http_method: {http_method}")

        return r

    def _parse_config(self, config):
        query = config.get('query', "")
        api_key = config.get('api_key', "")
        api_key_name = config.get('api_key_name', "")
        params = json.loads(config.get('params', "[]"))
        headers = json.loads(config.get('headers', "{}"))
        variables = json.loads(config.get('variables', "{}"))
        
        try:
            for param in params:
                if param['type'] == 'date':
                    if param['variable'] in query:
                        value = self._get_value(param['value'], param['unit']).strftime(param['format'])
                        variables[param['variable']] = value
                    else:
                        raise Exception("Params not informed in the input query")

                elif param['type'] == 'period':
                    if param['start_date']:
                        if param['start_date']['variable'] in query:
                            value = self._get_value(param['start_date']['value'], param['unit']).strftime(param['format'])
                            variables[param['start_date']['variable']] = value

                            if param['end_date']:
                                if param['end_date']['variable'] in query:
                                    value = self._get_value(param['end_date']['value'], param['unit']).strftime(param['format'])
                                    variables[param['end_date']['variable']] = value
                                else:
                                    raise Exception("Params not informed in the input query")
                            else:
                                raise Exception("Params end_date not informed")
                        else:
                            raise Exception("Params not informed in the input query")
                    else:
                        raise Exception("Params start_date not informed")
                else:
                    raise Exception("Params invalid")
            
            if len(query):
                body = {'query': query, 'variables': variables}
            else:
                raise Exception("Input query not informed in the URL")
            
            if len(headers):
                if len(api_key) and len(api_key_name):
                    headers[api_key_name] = api_key
            else:
                if len(api_key) and len(api_key_name):
                    headers = {api_key_name: api_key}
                else:
                    headers = {}

        except Exception as e:
            raise e

        return {
            "url": config.get("url"),
            "http_method": config.get("http_method", "POST"),
            "headers": headers,
            "body": body,
            "json_source": config.get("json_source", "root"),
            "json_field": config.get("json_field", ""),
        }


    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        parsed_config = self._parse_config(config)
        return [GraphqlRequest(parsed_config["url"], parsed_config["http_method"], parsed_config.get("headers"), parsed_config.get("body"), parsed_config.get("json_source"), parsed_config.get("json_field"),)]
