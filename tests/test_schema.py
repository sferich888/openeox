#!/bin/env python3

import json
import pytest
import logging

from jsonschema import validate
from jsonschema.protocols import Validator
from jsonschema.exceptions import ValidationError
from pathlib import Path
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource
from referencing.jsonschema import DRAFT202012 
from urllib.parse import urlparse


class TestJsonSchemaValidationWithRegistry:
    SCHEMAS = list(Path("schemas").glob("*.json"))
    registry = Registry()
    schema_uri_paths = []

    @pytest.fixture()
    def setup_registry(self, uri: str = "http://localhost/"):
        # Setup Logic
        logging.debug("Setting up registry")

        for path in self.SCHEMAS:
            resource = Resource(contents=json.loads(path.read_text()), specification=DRAFT202012)

            logging.debug(f"loading: {uri + str(path)}")
            self.schema_uri_paths.append(uri + str(path))

            self.registry = self.registry.with_resource(uri=uri+str(path), resource=resource).crawl()

        yield
        # Teardown logic
        logging.info("resetting registry")
        self.registry = Registry()


    def test_schema_load(self, setup_registry):
        logging.info(f"Validating that {len(self.schema_uri_paths)} schemas have loaded properly.")
        for uri_path in self.schema_uri_paths:
            assert self.registry.contents(uri_path) is not None


    def test_schema_validation(self, setup_registry):

        for uri, spec in self.registry.items():
            schema_file_name = urlparse(uri).path.split("/")[-1]

            sample_file_path = Path("schemas", "samples", schema_file_name)
            if sample_file_path.exists():
                logging.debug(f"Found a matching sample for the spec: {uri} within: {sample_file_path}")
                # logging.debug(self.registry.contents(uri))

                sample = json.loads(sample_file_path.read_text())
                try:
                    validate(sample, self.registry.contents(uri))
                    assert True
                    logging.info(f"Validated the sample '{sample_file_path}' against the spec: {uri}")
                except ValidationError as ve:
                    logging.error(ve)
                    assert False
            else:
                logging.debug(f"No matching sample for the spec: {uri}!")
