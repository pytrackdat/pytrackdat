PYTHON_KEYWORDS = ["False", "None", "True", "and", "as", "assert", "async", "await", "break", "class", "continue",
                   "def", "del", "else", "elif", "except", "finally", "for", "from", "global", "if", "import", "in",
                   "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"]

DATA_TYPES = ["auto key", "manual key", "foreign key", "integer", "boolean", "text", "float", "decimal", "date", "time"]


def field_to_py_code(field):
    if field in PYTHON_KEYWORDS:
        return field + "_field"
    return field
