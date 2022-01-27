#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import ndjson
import traceback
import smart_open
import numpy as np

from typing import Iterable
from genson import SchemaBuilder
from urllib.parse import urlparse
from .parse_path import ParsePath
from base_python.entrypoint import logger
from google.oauth2 import service_account
from airbyte_protocol import AirbyteStream
from google.cloud.storage import Client as GCSClient


class ConfigurationError(Exception):
    """Client mis-configured"""

class PermissionsError(Exception):
    """User don't have enough permissions"""

class Client():
    """Class that manages reading and parsing data from streams"""

    def __init__(self, dataset_name: str, url: str, provider: dict, format: str = None, reader_options: str = None, params: dict = "{}"):
        self.client = None
        self._dataset_name = dataset_name
        self._url = url
        self.params = json.loads(params) if isinstance(params, str) else params
        self._provider = provider
        self._storage_name = self._provider["storage"].upper()
        self._reader_format = format or "csv"
        self._reader_options = {}
        if reader_options:
            try:
                self._reader_options = json.loads(reader_options)
            except json.decoder.JSONDecodeError as err:
                error_msg = f"Failed to parse reader options {repr(err)}\n{reader_options}\n{traceback.format_exc()}"
                logger.error(error_msg)
                raise ConfigurationError(error_msg) from err
        if params:
            parser = ParsePath(self.url, self.params)
            self._url = parser.formated_path

    @property
    def stream_name(self) -> str:
        if self._dataset_name:
            return self._dataset_name
        return f"file_{self._provider['storage']}.{self._reader_format}"

    @property
    def is_folder(self) -> bool:
        return self._url.endswith("*")

    @property
    def binary_source(self):
        binary_formats = {"excel", "feather", "parquet", "orc", "pickle"}
        return self._reader_format in binary_formats

    @property
    def full_url(self):
        return f"{self.storage_scheme}{self.url}"

    @property
    def url(self) -> str:
        """Convert URL to remove the URL prefix (scheme)
        :return: the corresponding URL without URL prefix / scheme
        """
        parse_result = urlparse(self._url)
        if parse_result.scheme:
            return self._url.split("://")[-1]
        else:
            return self._url

    @property
    def storage_scheme(self) -> str:
        """Convert Storage Names to the proper URL Prefix
        :return: the corresponding URL prefix / scheme
        """
        storage_name = self._storage_name
        parse_result = urlparse(self._url)
        if storage_name == "GCS":
            return "gs://" 
        else:
            raise NotImplementedError(f"{storage_name} is not supported yet")
    
    def streams(self,file: str = None) -> Iterable:
        """Discovers available streams"""
        # TODO handle discovery of directories of multiple files instead
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": self._stream_properties(file),
        }

        yield AirbyteStream(name=self.stream_name, json_schema=json_schema)

    def read(self, fields: Iterable = None,file: str = None) -> Iterable[dict]:
        """Read data from the stream"""
        
        with self.open(binary=self.binary_source,file=file) as fp:
            if self._reader_format == "json" or self._reader_format == "jsonl":
                yield from self._load_nested_json(fp)
            else:
                fields = set(fields) if fields else None
                for df in self.load_dataframes(fp):
                    columns = fields.intersection(set(df.columns)) if fields else df.columns
                    df = df.replace(np.nan, "NaN", regex=True)
                    yield from df[columns].to_dict(orient="records")

    def list_files_in_folder(self) -> list:
        if not self.client:
            self.client = self._connect()

        if self._storage_name == "GCS":
            path = self.url.replace("*", "")
            bucket_name = path.split("/")[0]
            sub_folders = path.replace(f"{bucket_name}/","")
            bucket = self.client.get_bucket(bucket_name)
            files = [file.name.split("/")[-1] for file in list(bucket.list_blobs(prefix=sub_folders))]
            if files[0] == "":
                files.pop(0)
            return files
        else: 
            raise NotImplementedError("Listing files is only supported for GCS")

    def open(self,file: str = None,binary: bool = False) -> smart_open.open:
        if not file:
            file = self.full_url
            
        mode = "rb" if binary else "r"
        storage = self.storage_scheme
        url = self.url

        if storage == "gs://":
            return self._open_gcs_url(file,binary=binary)
        else:
            raise NotImplementedError(f"{storage} is not supported yet")

    def _open_gcs_url(self,file: str = None, binary: bool = False) -> object:
        mode = "rb" if binary else "r"
        client = self.client or self._connect()
        
        file = smart_open.open(file, transport_params=dict(client=client), mode=mode)
        return file

    def __enter__(self):
        return self._connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()

    def _connect(self):
        """Connect to the data source"""
        if self._storage_name == "GCS":
            service_account_json = self._provider.get("service_account_json")
            credentials = None
            if service_account_json:
                try:
                    credentials = json.loads(self._provider["service_account_json"])
                except json.decoder.JSONDecodeError as err:
                    error_msg = f"Failed to parse gcs service account json: {repr(err)}\n{traceback.format_exc()}"
                    logger.error(error_msg)
                    raise ConfigurationError(error_msg) from err

            if credentials:
                credentials = service_account.Credentials.from_service_account_info(credentials)
                client = GCSClient(credentials=credentials, project=credentials._project_id)
            else:
                client = GCSClient.create_anonymous_client()
        else: 
            raise NotImplementedError("Listing files is only supported for GCS")
        
        return client

    def _stream_properties(self,file: str = None) -> dict:
        if not file:
            file = self.full_url

        with self.open(binary=self.binary_source,file=file) as fp:
            if self._reader_format == "json" or self._reader_format == "jsonl":
                return self._load_nested_json_schema(fp)
            
            df_list = self.load_dataframes(fp, skip_data=False)
            fields = {}
            for df in df_list:
                for col in df.columns:
                    fields[col] = self.dtype_to_json_type(df[col].dtype)
            return {field: {"type": fields[field]} for field in fields}

    def _load_nested_json_schema(self, fp,list=False) -> dict:
        # Use Genson Library to take JSON objects and generate schemas that describe them,
        builder = SchemaBuilder()
        if self._reader_format == "jsonl":
            builder.add_object(ndjson.load(fp))
        else:
            builder.add_object(json.load(fp))

        result = builder.to_schema()
        if "items" in result and "properties" in result["items"]:
            result = result["items"]["properties"]
        return result
    
    def _load_nested_json(self, fp) -> list:
        if self._reader_format == "jsonl":
            result = ndjson.load(fp)
        else:
            result = json.load(fp)
            if not isinstance(result, list):
                result = [result]
        return result