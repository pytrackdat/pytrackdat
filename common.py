import re

PYTHON_KEYWORDS = ["False", "None", "True", "and", "as", "assert", "async", "await", "break", "class", "continue",
                   "def", "del", "else", "elif", "except", "finally", "for", "from", "global", "if", "import", "in",
                   "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"]

DATA_TYPES = ["auto key", "manual key", "integer", "float", "decimal", "boolean", "text", "date", "time", "foreign key"]


RE_DATE_YMD_D = re.compile("^[1-2]\d{3}-\d{1,2}-\d{1,2}$")
RE_DATE_YMD_S = re.compile("^[1-2]\d{3}/\d{1,2}/\d{1,2}$")
RE_DATE_DMY_D = re.compile("^\d{1,2}-\d{1,2}-[1-2]\d{3}$")
RE_DATE_DMY_S = re.compile("^\d{1,2}/\d{1,2}/[1-2]\d{3}$")

RE_MULTIPLE_UNDERSCORES = re.compile("[_]{2,}")


def field_to_py_code(field):
    field = field + "_field" if field in PYTHON_KEYWORDS else field
    field = re.sub(RE_MULTIPLE_UNDERSCORES, "_", field)
    return field


def to_relation_name(name):
    python_relation_name = "".join([n.capitalize() for n in name.split("_")])

    if python_relation_name in PYTHON_KEYWORDS:
        python_relation_name += "Class"

    return python_relation_name
