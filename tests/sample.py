import json

def generate_graphql_types(schema_path):
    """
    Generates GraphQL type definitions from a JSON schema file.

    Args:
        schema_path (str): Path to the JSON schema file.

    Returns:
        str: A string containing the GraphQL type definitions, or an error message.
    """
    types = ""

    # Load the JSON schema
    try:
        with open(schema_path, 'r') as f:
            schema_data = json.load(f)
    except FileNotFoundError:
        return "Error: Schema file not found."
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON in schema file: {e}"

    # Process definitions
    if "definitions" in schema_data:
        for def_name, definition in schema_data["definitions"].items():
            types += f"type {def_name} {{\n"
            if "properties" in definition:
                for prop_name, prop_def in definition["properties"].items():
                    # Basic type mapping (extend as needed)
                    if prop_def.get("type") == "string":
                        types += f"  {prop_name}: String"
                    elif prop_def.get("type") == "integer":
                        types += f"  {prop_name}: Int"
                    elif prop_def.get("type") == "number":
                        types += f"  {prop_name}: Float"
                    elif prop_def.get("type") == "boolean":
                        types += f"  {prop_name}: Boolean"
                    elif prop_def.get("type") == "array":
                        # Get the type of the items in the array.  Nested structures are hard
                        item_type = "String"  # Default
                        if "items" in prop_def:
                            if prop_def["items"].get("type") == "string":
                                item_type = "String"
                            elif prop_def["items"].get("type") == "integer":
                                item_type = "Int"
                            elif prop_def["items"].get("type") == "number":
                                item_type = "Float"
                            elif prop_def["items"].get("type") == "boolean":
                                item_type = "Boolean"
                            elif "$ref" in prop_def["items"]:
                                # Extract the name of the referenced definition
                                ref_name = prop_def["items"]["$ref"].split("/")[-1]
                                item_type = ref_name
                        types += f"  {prop_name}: [{item_type}]"
                    elif "$ref" in prop_def:
                         # Extract the name of the referenced definition
                         ref_name = prop_def["$ref"].split("/")[-1]
                         types += f"  {prop_name}: {ref_name}"

                    # Add nullability based on the required field.
                    if prop_name in definition.get("required", []):
                        types += "!"
                    types += "\n"
            types += "}\n\n"

    return types


def generate_schema(schema_file_paths: list = ['schemas/product-lifecycle.json', 'schemas/product.json']):
    generated_types = ''
    for schema_file in schema_file_paths:
        generated_types += generate_graphql_types(schema_file)

    # Add the base Query type.  This is very basic and would need to be expanded.
    generated_types += """
    type Query {
        #  Add root queries here,  e.g., to fetch specific data.
        lifecycle: LifeCycle
    }
    """
    return generated_types


if __name__ == "__main__":
    print(generate_schema())
