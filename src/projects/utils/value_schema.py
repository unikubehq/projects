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


def create_pydantic_schema(yaml_dict: dict, model_names: List) -> (dict, List):
    fields = {}
    for key, value in yaml_dict.items():
        type_ = type(value)
        if type_ is dict:
            sub_fields, model_names = create_pydantic_schema(value, model_names)
            name = get_model_name(key, model_names)
            model = create_model(name, **sub_fields)
            fields[key] = (Optional[model], None)
            model_names.append(name)
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
    return fields, model_names


def get_model_name(key: str, model_names: List) -> str:
    """Generates a name for a pydantic model, based on already taken model names."""
    if key not in model_names:
        return key
    counter = 1
    while key + str(counter) in model_names:
        counter += 1
    return key + str(counter)


def create_schema_json(yaml_dict):
    values_schema = create_model("HelmValuesJsonSchema", __base__=BaseModel, **create_pydantic_schema(yaml_dict, [])[0])
    return values_schema.schema()


def create_schema(content: dict) -> dict:
    return {"uri": "https://unikube/helm_json_schema", "fileMatch": ["*"], "schema": create_schema_json(content)}
