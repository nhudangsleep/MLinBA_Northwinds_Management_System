def schemas_prettier(data):
    prettified_schema = {}
    for row in data:
        schema_name, table_name, column_name, data_type, is_nullable, character_maximum_length, pk_name, is_auto_increment = row
        if schema_name not in prettified_schema:
            prettified_schema[schema_name] = {}
        if table_name not in prettified_schema[schema_name]:
            prettified_schema[schema_name][table_name] = []
        column_info = {
            "column_name": column_name,
            "data_type": data_type,
            "is_nullable": is_nullable,
            "character_maximum_length": character_maximum_length,
            "pk_name": pk_name,
            "is_auto_increment": is_auto_increment
        }
        prettified_schema[schema_name][table_name].append(column_info)
    print(prettified_schema)
    return prettified_schema
