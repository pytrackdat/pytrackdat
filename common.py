PYTHON_KEYWORDS = ["False", "None", "True", "and", "as", "assert", "async", "await", "break", "class", "continue",
                   "def", "del", "else", "elif", "except", "finally", "for", "from", "global", "if", "import", "in",
                   "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"]

DATA_TYPES = ["auto key", "manual key", "integer", "float", "decimal", "boolean", "text", "date", "time", "foreign key"]


def field_to_py_code(field):
    if field in PYTHON_KEYWORDS:
        return field + "_field"
    return field


def to_relation_name(name):
    python_relation_name = "".join([n.capitalize() for n in name.split("_")])

    if python_relation_name in PYTHON_KEYWORDS:
        python_relation_name += "Class"

    return python_relation_name
