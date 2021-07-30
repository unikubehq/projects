import logging
from typing import Any, List, Optional

import yaml
from kombu.utils import json
from pydantic import BaseModel, Field, create_model

logger = logging.getLogger("projects.schema_generation")


def create_json_value_schema_from_file(yaml_file_path):
    with open(yaml_file_path, "r") as f:
        return create_json_value_schema(f)


def create_json_value_schema_from_string(input: str):
    return create_json_value_schema(input)


def create_json_value_schema(input):
    content = yaml.safe_load(input)
    if not isinstance(content, dict):
        logger.info("Not parsable.")
        return

    return json.dumps(create_schema(content))


def create_pydantic_schema(yaml_dict: dict) -> dict:
    fields = {}
    for key, value in yaml_dict.items():
        type_ = type(value)
        if type_ is dict:
            sub_fields = create_pydantic_schema(value)
            model = create_model(key, **sub_fields)
            fields[key] = (Optional[model], None)
        elif type_ is list:
            if len(value):
                fields[key] = (Optional[List[type(value[0])]], None)
            else:
                fields[key] = (Optional[List[Any]], None)
        else:
            fields[key] = (
                Optional[type_],
                Field(
                    None,
                ),
            )
    return fields


def create_schema_json(yaml_dict):
    values_schema = create_model("HelmValuesJsonSchema", __base__=BaseModel, **create_pydantic_schema(yaml_dict))
    return values_schema.schema()


def create_schema(content: dict) -> dict:
    return {"uri": "https://unikube/helm_json_schema", "fileMatch": ["*"], "schema": create_schema_json(content)}
