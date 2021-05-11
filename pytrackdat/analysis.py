# PyTrackDat is a utility for assisting in online database creation.
# Copyright (C) 2018-2021 the PyTrackDat authors.
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

import argparse
import csv
import re
import sys

from typing import Dict, List, Optional, Sequence, Tuple

from pytrackdat import common as c


__all__ = [
    "AnalysisError",
    "infer_column_type",
    "create_design_file_rows_from_inference",
    "analyze_csv",
    "analyze_entry",
]


ALTERNATE_THRESHOLD = 0.5
MAX_CHOICES = 16
MAX_CHOICE_LENGTH = 24
CHAR_FIELD_MAX_LENGTH = 48
CHAR_FIELD_LENGTH = 128


class AnalysisError(Exception):
    pass


def strip_blank_fields(fields: tuple) -> tuple:
    blank_tail = len(fields)
    while blank_tail > 0 and fields[blank_tail-1].strip() == "":
        blank_tail -= 1

    return fields[:blank_tail]


def infer_column_type(
    relation: str,
    name: str,
    col: Sequence[str],
    keys: Optional[Dict[str, Tuple[str, Sequence]]] = None
) -> Dict:
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

        if re.match(c.RE_INTEGER, str_v) or re.match(c.RE_INTEGER_HUMAN, str_v):
            integer_values += 1
            integer_values_set.add(int(re.sub(c.RE_NUMBER_GROUP_SEPARATOR, "", str_v)))

        elif re.match(c.RE_DECIMAL, str_v.lower()) or re.match(c.RE_DECIMAL_HUMAN, str_v.lower()):
            decimal_values += 1
            max_seen_decimals = max(
                max_seen_decimals,
                (len(re.sub(c.RE_NUMBER_GROUP_SEPARATOR, "", str_v).split(".")[-1].split("e")[0])
                 if "." in str_v else -1)
            )

            if "e" in str_v:
                float_values += 1

        else:
            non_numeric_values.add(str_v)

            if any(re.match(df[0], str_v) is not None for df in c.DATE_FORMATS):
                date_values += 1

            elif any(re.match(df[0], str_v) is not None for df in c.TIME_FORMATS):
                time_values += 1

            else:
                other_values.add(str_v)

        max_seen_length = max(max_seen_length, len(str_v))
        all_values.add(str_v)
        all_values_counts[str_v] = all_values_counts.get(str_v, 0) + 1

    # Keys:
    #  - If keys aren't specified or this field is in fact the key, allow the key type to be inferred.

    if len(all_values) == len(col) and "" not in all_values and (keys is None or
                                                                 keys.get(relation, (None, None))[0] == name):
        detected_type = c.DT_MANUAL_KEY
        nullable = False
        is_key = True

    # TODO: Infer foreign keys for non-integers??? When do we infer foreign keys vs. ints?

    # Integers:

    elif integer_values == len(col):
        detected_type = c.DT_INTEGER
        nullable = False

    elif integer_values > 0 and len(non_numeric_values) == 1 and decimal_values == 0 \
            and not (len(integer_values_set) == 2 and 0 in integer_values_set and 1 in integer_values_set):
        detected_type = c.DT_INTEGER
        nullable = True
        # TODO: DO WE WANT NULL VALUES HERE?

    elif integer_values > 0 and len(non_numeric_values) > 1 and ((integer_values / len(col)) >= ALTERNATE_THRESHOLD):
        detected_type = c.DT_INTEGER
        nullable = True
        include_alternate = True

    # Decimals: TODO: more

    elif decimal_values > 0 and len(non_numeric_values) in (0, 1):
        # Integer or decimal values -> use a decimal field.
        # TODO: Find number of digits!!!
        detected_type = c.DT_DECIMAL
        nullable = (len(non_numeric_values) == 1)
        max_length = max_seen_length + max_seen_decimals + 4

    # Floats: TODO: more

    elif float_values > 0 and len(non_numeric_values) in (0, 1):
        # Integer, decimal or float values in column -> use a float field.
        detected_type = c.DT_FLOAT
        nullable = (len(non_numeric_values) == 1)

    # Dates:

    elif date_values == len(col):
        detected_type = c.DT_DATE
        nullable = False
        # TODO: Detect date format and make additional settings with date format

    elif date_values > 0 and len(other_values) == 1:
        detected_type = c.DT_DATE
        nullable = True
        null_values = list(other_values)[0]

    # Times:

    elif time_values == len(col):
        detected_type = c.DT_TIME
        nullable = False
        # TODO: Detect time format and make additional settings with time format

    elif time_values > 0 and len(other_values) == 1:
        detected_type = c.DT_TIME
        nullable = True
        null_values = list(other_values)[0]

    # Enums:

    elif (len([a for a in all_values if a.strip() != ""]) < MAX_CHOICES and max_seen_length < MAX_CHOICE_LENGTH and
          sum(v for a, v in all_values_counts.items() if a.strip() != "") >= 2 * len(all_values)):
        detected_type = c.DT_TEXT
        nullable = "" in all_values
        choices = sorted(all_values)
        in_choices = {ch.lower() for ch in choices}
        max_length = max_seen_length * 2

        # Booleans:
        if (len(choices) == 2 or (len(choices) == 3 and nullable)) and any(tv in in_choices and fv in in_choices
                                                                           for tv, fv in c.BOOLEAN_TF_PAIRS):
            detected_type = c.DT_BOOLEAN
            null_values = [ch for ch in choices if ch.lower() not in c.BOOLEAN_TRUE_VALUES + c.BOOLEAN_FALSE_VALUES]

    # Text

    # TODO: I don't like this logic

    elif integer_values < max(len(col) / 10, 10) or len(non_numeric_values) >= 10:
        detected_type = c.DT_TEXT
        nullable = False
        if max_seen_length <= CHAR_FIELD_MAX_LENGTH and "note" not in name and "comment" not in name:
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
    f_type = inference["detected_type"]

    choices = (inference["choices"] if inference["choices"] and f_type != c.DT_BOOLEAN else None)

    inferred_field = c.RelationField(
        csv_names=(old_name,),  # Old CSV / field name(s)
        name=new_name,  # New field name (in database)
        data_type=f_type,  # Detected data type
        nullable=inference["nullable"],  # Whether the field is nullable
        null_values=inference["null_values"],  # What value(s) will become null in the database
        default="",  # The default value for the field (optional, null/blank if left empty)
        description="!fill me in!",  # Field description
        show_in_table=(f_type not in {c.DT_TEXT, *c.GIS_DATA_TYPES} or
                       (f_type == c.DT_TEXT and (inference["choices"] or inference["max_length"] > 0))),
        additional_fields=(
            # IF DECIMAL: Max length and decimal placement:
            *((inference["max_length"], inference["max_seen_decimals"]) if f_type == c.DT_DECIMAL
              else ()),
            # IF TEXT/ENUM: Max length:
            *((inference["max_length"],) if f_type == c.DT_TEXT and inference["max_length"] > 0 else ()),
            # IF ENUM: Choices:
            *((f"{c.DESIGN_SEPARATOR} ".join(choices),) if choices is not None else ()),
        ),
        choices=choices,  # Not used here?
    )

    design_file_rows = [inferred_field.as_design_file_row()]
    if inference["include_alternate"]:
        design_file_rows.append(inferred_field.make_alternate().as_design_file_row())

    return design_file_rows


def extract_data_from_relation_file(rf):
    data = []
    with open(rf, "r", encoding="utf-8-sig") as ff:
        data_reader = csv.reader(ff, delimiter=",")

        # TODO: strip or no? might cause errors but could handle in import.
        fields = strip_blank_fields(tuple(f for f in next(data_reader)))

        if len(fields) == 0:
            c.exit_with_error("Error: No fields detected")

        d = next(data_reader)
        while True:
            try:
                row = [x.strip() for x in d]
                if any(cell != "" for cell in row):
                    # Skip blank rows, they're likely CSV artifacts
                    data.append(row)
                d = next(data_reader)
            except StopIteration:
                break

        if fields is None:
            fields = []

    return data, fields


def analyze_csv(relations: Tuple[Tuple[str, str], ...], output_cb=print):
    relation_names = [r[0] for r in relations]

    if len(set(relation_names)) < len(relation_names):
        duplicates = "\t".join(set(r for r in relation_names if len([r2 for r2 in relation_names if r2 == r]) > 1))
        raise AnalysisError(f"You cannot use the same relation name(s) for more than one table:\n\t{duplicates}")

    keys = {}

    # Pass 1: Find key candidates and possible foreign keys
    for rn, rf in relations:
        output_cb(f"Finding keys for relation '{rn}'...")

        data, fields = extract_data_from_relation_file(rf)

        for i, f in enumerate(fields):
            new_name = c.field_to_py_code(f)

            col = tuple(d[i] for d in data)
            inference = infer_column_type(rn, new_name, col)

            if inference["is_key"]:
                keys[rn] = (new_name, col)
                output_cb(f"    Field '{new_name}' identified as a key")
                break

        output_cb()

    # Pass 2: Determine other column data types
    design_file_rows = []
    for rn, rf in relations:
        output_cb(f"Detecting types for fields in relation '{rn}'...")

        data, fields = extract_data_from_relation_file(rf)

        design_file_rows.append([rn, "new field name", "data type", "nullable?", "null values", "default",
                                 "description", "show in table?", "additional fields..."])

        new_design_file_rows = []

        if rn not in keys:
            output_cb(f"\n    Warning: No primary key found for relation '{rn}'. If you have a field you "
                      f"\n             think should be the primary key (row identifier), this is an indication"
                      f"\n             that there may be duplicate values. \n"
                      f"\n             Adding an automatic key instead....")  # TODO

            # Add automatic primary key to design file
            new_design_file_rows = [c.RelationField(
                csv_names=(),  # CSV names (blank)
                name=f"{rn}_id",  # "new" (database) name
                data_type=c.DT_AUTO_KEY,  # auto primary key type
                nullable=False,  # not nullable - primary key
                null_values=(),  # no null values
                default="",  # no default value
                description="Unique identifier automatically generated by the database",  # auto-generated description
                show_in_table=True,  # show primary key in table list view
                additional_fields=(),  # no additional fields
            ).as_design_file_row()]

        for i, f in enumerate(fields):
            new_name = c.field_to_py_code(f)

            col = tuple(d[i] for d in data)
            inference = infer_column_type(rn, new_name, col, keys)

            design_file_row = create_design_file_rows_from_inference(f, new_name, inference)
            new_design_file_rows.extend(design_file_row)

            output_cb("    Field '{}':\n        Type: '{}'\n        Nullable: {}{}{}".format(
                f,
                inference["detected_type"],
                inference["nullable"],
                f"\n        Choices: {inference['choices']}" if inference["choices"] else "",
                "\n        With alternate" if inference["include_alternate"] else ""
            ))

        new_design_file_rows.append([])
        design_file_rows.extend(new_design_file_rows)
        output_cb()

    max_length = max(len(r) for r in design_file_rows)
    for r in design_file_rows:
        r.extend([""] * (max_length - len(r)))  # Pad out row with blank columns if needed
        yield r

    output_cb(f"Analyzed {len(relations)} relations.")


def analyze_entry(args: argparse.Namespace):
    c.print_license()

    design_file = args.design_out
    name_file_pairs = args.name_file_pairs

    # args = sys.argv[1:]

    if len(name_file_pairs) % 2 or len(name_file_pairs) < 2:
        print("Usage: pytrackdat analyze --design-out design_out.csv relation_1_name file1.csv "
              "[relation_2_name file2.csv] ...")
        exit(1)

    # Split pairs of file name, relation name
    relation_names = name_file_pairs[::2]
    relations = tuple(zip(map(str.lower, relation_names), name_file_pairs[1::2]))

    try:
        g = analyze_csv(relations)
        with open(design_file, "w", newline="") as df:
            design_writer = csv.writer(df, delimiter=",")
            for r in g:
                design_writer.writerow(r)

            print(f"    Wrote design file to '{design_file}'...\n")

    except AnalysisError as e:
        print(str(e), file=sys.stderr)
        exit(1)

    except IOError:
        print("\nError: Could not write to design file.\n", file=sys.stderr)
        exit(1)
