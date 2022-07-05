
def check_structure(object, structure, root):
    """
    ensures the structures are the same. none values are not checked for type

    @param object - the object being checked
    @param structure - the actual structure

    @return returns an obj with "missingKeys" and "wrongType"
    """
    missing_keys = []
    wrong_type = []
    for key, structure_value in structure.items():
        path = root + " > " + key
        if key not in object:
            missing_keys.append(path)
            continue
        if (isinstance(structure_value, float) and
            isinstance(object[key], int)):  # some complements are floats (averaged)
            object[key] = float(object[key])
        if not isinstance(structure_value, float) and not isinstance(object[key], type(structure_value)):
            wrong_type.append({
                "path": path,
                "actualType": type(object[key]),
                "requiredType": type(structure_value)
            })
            continue
        if (type(structure_value) is dict):
            result = check_structure(object[key], structure_value, path)
            missing_keys += result["missingKeys"]
            wrong_type += result["wrongType"]
    return {
        "missingKeys": missing_keys,
        "wrongType": wrong_type
    }
