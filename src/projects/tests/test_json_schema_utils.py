import json

from django.test import TestCase

from projects.utils.value_schema import create_json_value_schema_from_file, create_json_value_schema_from_string


class JsonSchemaTest(TestCase):
    def test_simple_yaml(self):
        yaml = """
        key: value
        anotherKey: anotherValue
        """

        result = json.loads(create_json_value_schema_from_string(yaml))
        self.assertTrue("schema" in result)
        schema = result["schema"]
        self.assertTrue("properties" in schema)
        properties = schema["properties"]
        self.assertTrue("key" in properties)
        self.assertTrue("type" in properties["key"])
        self.assertEqual(properties["key"]["type"], "string")
        self.assertTrue("anotherKey" in properties)
        self.assertTrue("type" in properties["anotherKey"])
        self.assertEqual(properties["anotherKey"]["type"], "string")

    def test_yaml_with_boolean(self):
        yaml = """
        key: true
        """

        result = json.loads(create_json_value_schema_from_string(yaml))
        self.assertTrue("schema" in result)
        schema = result["schema"]
        self.assertTrue("properties" in schema)
        properties = schema["properties"]
        self.assertTrue("key" in properties)
        self.assertTrue("type" in properties["key"])
        self.assertEqual(properties["key"]["type"], "boolean")

    def test_yaml_with_number(self):
        yaml = """
        key: 12
        """
        result = json.loads(create_json_value_schema_from_string(yaml))
        self.assertTrue("schema" in result)
        schema = result["schema"]
        self.assertTrue("properties" in schema)
        properties = schema["properties"]
        self.assertTrue("key" in properties)
        self.assertTrue("type" in properties["key"])
        self.assertEqual(properties["key"]["type"], "integer")

    def test_invalid_string_input(self):
        yaml = """
        key
        """
        self.assertEqual(create_json_value_schema_from_string(yaml), None)

    def test_yaml_with_list(self):
        yaml = """
        anotherKey:
            - item1
            - item2
            - item3
        """

        result = json.loads(create_json_value_schema_from_string(yaml))
        self.assertTrue("schema" in result)
        schema = result["schema"]
        self.assertTrue("properties" in schema)
        properties = schema["properties"]
        self.assertTrue("anotherKey" in properties)
        self.assertTrue("type" in properties["anotherKey"])
        self.assertEqual(properties["anotherKey"]["type"], "array")

    def test_yaml_with_empty_list(self):
        yaml = """
        anotherKey:
            - item1
            - item2
            - item3
        emptyList: []
        """

        result = json.loads(create_json_value_schema_from_string(yaml))
        self.assertTrue("schema" in result)
        schema = result["schema"]
        self.assertTrue("properties" in schema)
        properties = schema["properties"]
        self.assertTrue("anotherKey" in properties)
        self.assertTrue("type" in properties["anotherKey"])
        self.assertEqual(properties["anotherKey"]["type"], "array")
        self.assertTrue("emptyList" in properties)
        self.assertTrue("type" in properties["emptyList"])
        self.assertEqual(properties["emptyList"]["type"], "array")
        self.assertEqual(len(properties["emptyList"]["items"].keys()), 0)

    def test_yaml_with_object_list(self):
        yaml = """
        anotherKey:
            - name: name1
              someValue1: value1
            - name: name2
              someValue2: value2
        """
        result = json.loads(create_json_value_schema_from_string(yaml))
        self.assertTrue("schema" in result)
        schema = result["schema"]
        self.assertTrue("properties" in schema)
        properties = schema["properties"]
        self.assertTrue("anotherKey" in properties)
        self.assertTrue("type" in properties["anotherKey"])
        self.assertEqual(properties["anotherKey"]["type"], "array")
        self.assertTrue("type" in properties["anotherKey"]["items"])
        self.assertEqual(properties["anotherKey"]["items"]["type"], "object")

    def test_yaml_with_multiple_objects(self):
        yaml = """
        key:
            objectKey: test
        anotherKey:
            name: name1
        """

        result = json.loads(create_json_value_schema_from_string(yaml))
        self.assertTrue("schema" in result)
        schema = result["schema"]
        self.assertTrue("properties" in schema)
        self.assertTrue("definitions" in schema)
        properties = schema["properties"]
        definitions = schema["definitions"]
        self.assertTrue("key" in properties)
        self.assertTrue("$ref" in properties["key"])
        self.assertTrue("anotherKey" in properties)
        self.assertTrue("$ref" in properties["anotherKey"])

        self.assertTrue("key" in definitions)
        self.assertTrue("properties" in definitions["key"])
        self.assertTrue("objectKey" in definitions["key"]["properties"])

        self.assertTrue("anotherKey" in definitions)
        self.assertTrue("properties" in definitions["anotherKey"])
        self.assertTrue("name" in definitions["anotherKey"]["properties"])

    def test_yaml_schema_creation_from_file(self):
        file_path = "projects/tests/example.yaml"
        result = json.loads(create_json_value_schema_from_file(file_path))
        self.assertTrue("schema" in result)
        schema = result["schema"]
        self.assertTrue("properties" in schema)
        properties = schema["properties"]
        self.assertTrue("test" in properties)
        self.assertTrue("$ref" in properties["test"])
