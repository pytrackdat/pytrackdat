# PyTrackDat is a utility for assisting in online database creation.
# Copyright (C) 2018-2020 the PyTrackDat authors.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact information:
#     David Lougheed (david.lougheed@gmail.com)

# To lowercase
# Replace whitespace with underline
# Analyze domain and find out:
#    integer with one other value -> nullable integer
#    integer with no other value -> integer
#    decimal with constant digits -> decimal (max: length plus 2)
#    y/n, t/f, true/false -> boolean
#    y/n/u, y/n/blank, etc. -> nullable boolean
#    mm/dd/yyyy, dd/mm/yyyy, yyyy-mm-dd -> date (if ONE other value that doesn't match, nullable) TODO
#    HH:MM pm, HH:MMpm, HH:MM, etc -> time (if ONE other value that doesn't match, nullable) TODO
#    text where the choices are way less than the number of rows -> max length text choice field
#    highly deviant text (excluding blanks) -> text field

# LIMITATION: memory must be enough to ingest the CSV file to analyze

import csv
import re
import sys

from typing import Dict, List

from .common import *


__all__ = ["infer_column_type", "create_design_file_rows_from_inference", "main"]


ALTERNATE_THRESHOLD = 0.5
MAX_CHOICES = 16
MAX_CHOICE_LENGTH = 24
CHAR_FIELD_MAX_LENGTH = 48
CHAR_FIELD_LENGTH = 128


def strip_blank_fields(fields: tuple) -> tuple:
    blank_tail = len(fields)
    while blank_tail > 0 and fields[blank_tail-1].strip() == "":
        blank_tail -= 1

    return fields[:blank_tail]


def infer_column_type(col: List[str], key_found: bool) -> Dict:
    detected_type = "unknown"
    nullable = False
    null_values = []
    choices = []
    max_length = -1
    is_key = False
    include_alternate = False

    integer_values = 0
    decimal_values = 0
    float_values = 0

    integer_values_set = set()

    all_values = set()
    all_values_counts = {}

    date_values = 0
    time_values = 0

    non_numeric_values = set()
    other_values = set()

    max_seen_length = -1
    max_seen_decimals = -1

    for v in col:
        str_v = str(v).strip()

        if re.match(RE_INTEGER, str_v) or re.match(RE_INTEGER_HUMAN, str_v):
            integer_values += 1
            integer_values_set.add(int(re.sub(RE_NUMBER_GROUP_SEPARATOR, "", str_v)))

        elif re.match(RE_DECIMAL, str_v.lower()) or re.match(RE_DECIMAL_HUMAN, str_v.lower()):
            decimal_values += 1
            max_seen_decimals = max(
                max_seen_decimals,
                (len(re.sub(RE_NUMBER_GROUP_SEPARATOR, "", str_v).split(".")[-1].split("e")[0])
                 if "." in str_v else -1)
            )

            if "e" in str_v:
                float_values += 1

        else:
            non_numeric_values.add(str_v)

            if any(re.match(df[0], str_v) is not None for df in DATE_FORMATS):
                date_values += 1

            elif any(re.match(df[0], str_v) is not None for df in TIME_FORMATS):
                time_values += 1

            else:
                other_values.add(str_v)

        max_seen_length = max(max_seen_length, len(str_v))
        all_values.add(str_v)
        all_values_counts[str_v] = all_values_counts.get(str_v, 0) + 1

    # Keys:

    if len(all_values) == len(col) and "" not in all_values and not key_found:
        detected_type = "manual key"
        nullable = False
        is_key = True

    # Integers:

    elif integer_values == len(col):
        detected_type = "integer"
        nullable = False

    elif integer_values > 0 and len(non_numeric_values) == 1 and decimal_values == 0 \
            and not (len(integer_values_set) == 2 and 0 in integer_values_set and 1 in integer_values_set):
        detected_type = "integer"
        nullable = True
        # TODO: DO WE WANT NULL VALUES HERE?

    elif integer_values > 0 and len(non_numeric_values) > 1 and ((integer_values / len(col)) >= ALTERNATE_THRESHOLD):
        detected_type = "integer"
        nullable = True
        include_alternate = True

    # Decimals: TODO: more

    elif decimal_values > 0 and len(non_numeric_values) in (0, 1):
        # Integer or decimal values -> use a decimal field.
        # TODO: Find number of digits!!!
        detected_type = "decimal"
        nullable = (len(non_numeric_values) == 1)
        max_length = max_seen_length + max_seen_decimals + 4

    # Floats: TODO: more

    elif float_values > 0 and len(non_numeric_values) in (0, 1):
        # Integer, decimal or float values in column -> use a float field.
        detected_type = "float"
        nullable = (len(non_numeric_values) == 1)

    # Dates:

    elif date_values == len(col):
        detected_type = "date"
        nullable = False
        # TODO: Detect date format and make additional settings with date format

    elif date_values > 0 and len(other_values) == 1:
        detected_type = "date"
        nullable = True
        null_values = list(other_values)[0]

    # Times:

    elif time_values == len(col):
        detected_type = "time"
        nullable = False
        # TODO: Detect time format and make additional settings with time format

    elif time_values > 0 and len(other_values) == 1:
        detected_type = "time"
        nullable = True
        null_values = list(other_values)[0]

    # Enums:

    elif (len([a for a in all_values if a.strip() != ""]) < MAX_CHOICES and max_seen_length < MAX_CHOICE_LENGTH and
          sum(v for a, v in all_values_counts.items() if a.strip() != "") >= 2 * len(all_values)):
        detected_type = "text"
        nullable = ("" in all_values)
        choices = sorted(all_values)
        in_choices = {c.lower() for c in choices}
        max_length = max_seen_length * 2

        # Booleans:
        if (len(choices) == 2 or (len(choices) == 3 and nullable)) and any(tv in in_choices and fv in in_choices
                                                                           for tv, fv in BOOLEAN_TF_PAIRS):
            detected_type = "boolean"
            null_values = [c for c in choices if c.lower() not in BOOLEAN_TRUE_VALUES + BOOLEAN_FALSE_VALUES]

    # Text

    # TODO: I don't like this logic

    elif integer_values < max(len(col) / 10, 10) or len(non_numeric_values) >= 10:
        detected_type = "text"
        nullable = False
        if max_seen_length <= CHAR_FIELD_MAX_LENGTH:
            max_length = CHAR_FIELD_LENGTH

    return {
        "detected_type": detected_type,
        "nullable": nullable,
        "null_values": tuple(null_values),
        "choices": tuple(choices),
        "max_length": max_length,
        "is_key": is_key,
        "include_alternate": include_alternate,

        "max_seen_decimals": max_seen_decimals
    }


def create_design_file_rows_from_inference(old_name: str, new_name: str, inference: Dict) -> List[List[str]]:
    design_file_rows = [[
        old_name,  # Old field name
        new_name,  # New field name (in database)
        inference["detected_type"],  # Detected data type
        str(inference["nullable"]).lower(),  # Whether the field is nullable
        "; ".join(inference["null_values"]),  # What value(s) will become null in the database
        "",  # The default value for the field (optional, null/blank if left empty)
        "!fill me in!",  # Field description
        *[m for m in [max(inference["max_length"], 2), max(inference["max_seen_decimals"], 1)]
          if inference["detected_type"] == "decimal"],
        # IF TEXT/ENUM: max length:
        *[m for m in [inference["max_length"]]
          if inference["detected_type"] == "text" and inference["max_length"] > 0],
        # IF ENUM: Choices:
        *["; ".join([c for c in inference["choices"]
                     if len(inference["choices"]) > 0 and inference["detected_type"] != "boolean"])],
    ]]

    if inference["include_alternate"]:
        design_file_rows.append([
            old_name,
            new_name + "_alt",  # New field name (in database; alternate)
            "text",  # Alternate fields are always text, possibly with choices
            "false",  # Alt. fields cannot be null
            "",
            "",
            "!fill me in!"
        ])

    return design_file_rows


def main():
    print_license()

    args = sys.argv[1:]

    if len(args) % 2 != 1 or len(args) < 3:
        print("Usage: ptd-analyze design_out.csv relation_1_name file1.csv [relation_2_name file2.csv] ...")
        exit(1)

    design_file = args[0]  # Name for output
    relations = tuple(zip(args[1::2], map(str.lower, args[2::2])))  # Split pairs of file name, relation name

    if len(set(args[1::2])) < len(args[1::2]):
        print("Error: You cannot use the same relation name(s) for more than one table:")

        duplicates = set(r for r in args[1::2] if len([r2 for r2 in args[1::2] if r2 == r]) > 1)
        for r in duplicates:
            print("\t{}".format(r))

        exit(1)

    design_file_rows = []
    for rn, rf in relations:
        print("Detecting types for fields in relation '{}'...".format(rn))

        data = []
        with open(rf, "r", encoding="utf-8-sig") as ff:
            data_reader = csv.reader(ff, delimiter=",")

            # TODO: strip or no? might cause errors but could handle in import.
            fields = strip_blank_fields(tuple(f for f in next(data_reader)))

            if len(fields) == 0:
                exit_with_error("Error: No fields detected")

            d = next(data_reader)
            while True:
                try:
                    row = list(map(lambda x: x.strip(), d))
                    if len([c for c in row if c != ""]) > 0:
                        # Skip blank rows, they're likely CSV artifacts
                        data.append(list(map(lambda x: x.strip(), d)))
                    d = next(data_reader)
                except StopIteration:
                    break

            if fields is None:
                fields = []

        if len(fields) == 0:
            continue

        design_file_rows.append([rn, "new field name", "data type", "nullable?", "null values", "default",
                                 "description", "additional fields..."])

        new_design_file_rows = []

        key_found = False

        for i, f in zip(range(len(fields)), fields):
            new_name = field_to_py_code(f)

            col = [d[i] for d in data]
            inference = infer_column_type(col, key_found)

            key_found = key_found or inference["is_key"]

            design_file_row = create_design_file_rows_from_inference(f, new_name, inference)
            new_design_file_rows.extend(design_file_row)

            print("    Field '{}':\n        Type: '{}'\n        Nullable: {}{}{}".format(
                f,
                inference["detected_type"],
                inference["nullable"],
                "\n        Choices: {}".format(inference["choices"]) if len(inference["choices"]) > 0 else "",
                "\n        With alternate" if inference["include_alternate"] else ""
            ))

        if not key_found:
            print("\n    Warning: No primary key found for relation '{}'. If you have a field you "
                  "\n             think should be the primary key (row identifier), this is an indication"
                  "\n             that there may be duplicate values. \n"
                  "\n             Adding an automatic key instead....".format(rn))  # TODO

            new_design_file_rows = [["", "{}_id".format(rn), "auto key", "false", "", "",
                                     "Unique identifier automatically generated by the database"],
                                    *new_design_file_rows]

        new_design_file_rows.append([])
        design_file_rows.extend(new_design_file_rows)
        print()

    try:
        with open(design_file, "w", newline="") as df:
            design_writer = csv.writer(df, delimiter=",")
            max_length = max(len(r) for r in design_file_rows)

            for r in design_file_rows:
                r.extend([""] * (max_length - len(r)))  # Pad out row with blank columns if needed
                design_writer.writerow(r)

            print("    Wrote design file to '{}'...\n".format(design_file))

        print("Analyzed {} relations.".format(len(relations)))

    except IOError:
        print("\nError: Could not write to design file.\n")
        exit(1)


if __name__ == "__main__":
    main()
