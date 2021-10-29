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


import unittest

from source_graphql import SourceHttpRequest
from unittest.mock import patch, Mock
from datetime import date

class TestSourceHttpRequest(unittest.TestCase):
    def test_query_random_provider_parse_config_success(self):
        config = {
            "url": "https://swapi-graphql.netlify.app/.netlify/functions/index",
            "http_method": "POST",
            "params": "[{\"input_query\": \"query Root($after: String, $first: Int) { allFilms(after: $after, first: $first) { pageInfo { hasNextPage hasPreviousPage startCursor endCursor } totalCount films { title episodeID openingCrawl director producers releaseDate } } }\", \"variables\": {}}]",
            "json_source": "field",
            "json_field": "root.allFilms.films"
        }

        source = SourceHttpRequest()
        actual = source._parse_config(config)
        expected = {
            "url": "https://swapi-graphql.netlify.app/.netlify/functions/index",
            "http_method": "POST",
            "headers": {},
            "body": {"query": "query Root($after: String, $first: Int) { allFilms(after: $after, first: $first) { pageInfo { hasNextPage hasPreviousPage startCursor endCursor } totalCount films { title episodeID openingCrawl director producers releaseDate } } }", "variables": {}},
            "json_source": "field",
            "json_field": "root.allFilms.films"
        }
        self.assertEqual(expected, actual)

    def test_query_parse_config_success(self):
        config = {
            "url": "https://md.uat.idealtech.services/",
            "http_method": "POST",
            "api_key": "tPS4XotJcf4DcW74vU6Z6ajtqcLwJs0z9A8gia52",
            "api_key_name": "x-api-key",
            "params": "[{\"input_query\": \"query { corporateActionCodes { totalCount nodes { code description } } }\"}]",
            "json_source": "field",
            "json_field": "root.corporateActionCodes.nodes"
        }

        source = SourceHttpRequest()
        actual = source._parse_config(config)
        expected = {
            "url": "https://md.uat.idealtech.services/",
            "http_method": "POST",
            "headers": {"x-api-key": "tPS4XotJcf4DcW74vU6Z6ajtqcLwJs0z9A8gia52"},
            "body": {"query": "query { corporateActionCodes { totalCount nodes { code description } } }", "variables": {}},
            "json_source": "field",
            "json_field": "root.corporateActionCodes.nodes"
        }
        self.assertEqual(expected, actual)

    def test_get_host_success(self):
        url = "https://swapi-graphql.netlify.app/.netlify/functions/index"

        source = SourceHttpRequest()
        actual = source._get_host(url)
        expected = "swapi-graphql.netlify.app"
        self.assertEqual(expected, actual)
