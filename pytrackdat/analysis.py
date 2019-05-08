# PyTrackDat is a utility for assisting in online database creation.
# Copyright (C) 2018-2019 the PyTrackDat authors.
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

from .common import *


def main():
    print_license()

    args = sys.argv[1:]

    if len(args) % 2 != 1 or len(args) < 3:
        print("Usage: ptd-analyze design_out.csv relation_1_name file1.csv [relation_2_name file2.csv] ...")
        exit(1)

    design_file = args[0]  # Name for output
    relations = zip(args[1::2], map(str.lower, args[2::2]))  # Split pairs of file name, relation name

    if len(set(args[1::2])) < len(args[1::2]):
        print("Error: You cannot use the same relation name(s) for more than one table:")

        duplicates = set([r for r in args[1::2] if len([r2 for r2 in args[1::2] if r2 == r]) > 1])
        for r in duplicates:
            print("\t{}".format(r))

        exit(1)

    with open(design_file, "w") as df:
        design_writer = csv.writer(df, delimiter=",")
        for rn, rf in relations:
            data = []
            with open(rf, "r", encoding="utf-8-sig") as ff:
                data_reader = csv.reader(ff, delimiter=",")
                fields = [f for f in next(data_reader) if f != ""]

                d = next(data_reader)
                while True:
                    try:
                        data.append(list(map(lambda x: x.strip(), d)))
                        d = next(data_reader)
                    except StopIteration:
                        break

                if fields is None:
                    fields = []

            if len(fields) == 0:
                continue

            design_writer.writerow([rn, "new field name", "data type", "nullable?", "null values", "default",
                                    "description", "additional fields..."])

            key_found = False

            for i, f in zip(range(len(fields)), fields):
                new_name = field_to_py_code(re.sub(r"[^\w]+", "", re.sub(r"\s+", "_", f.lower())))
                detected_type = "unknown"
                nullable = False
                null_values = []

                col = [d[i] for d in data]

                integer_values = 0
                decimal_values = 0
                float_values = 0
                all_values = set()
                date_values = 0
                time_values = 0
                other_values = set()
                other_values_seen = 0
                choices = []
                max_seen_length = -1
                max_seen_decimals = -1
                max_length = -1
                include_alternate = False

                for v in col:
                    str_v = str(v).strip()
                    if re.match(r"^([+-]?[1-9]\d*|0)$", str_v):
                        integer_values += 1
                    elif re.match(r"^[-+]?[0-9]*\.?[0-9]+(e[-+]?[0-9]+)?$", str_v):
                        decimal_values += 1
                        max_seen_decimals = max(max_seen_decimals, (len(str_v.split(".")[-1].split("e")[0])
                                                                    if "." in str_v else -1))
                        if "e" in str_v:
                            float_values += 1
                    else:
                        other_values.add(str_v)
                        other_values_seen += 1

                    max_seen_length = max(max_seen_length, len(str_v))
                    all_values.add(str_v)

                    if re.match(RE_DATE_YMD_D, str_v) or \
                            re.match(RE_DATE_YMD_S, str_v) or \
                            re.match(RE_DATE_DMY_D, str_v) or \
                            re.match(RE_DATE_DMY_S, str_v):
                        date_values += 1

                    if re.match(r"^\d{1,2}:\d{2}(:\d{2})?$", str_v):
                        time_values += 1

                # Keys:

                if len(all_values) == len(data) and "" not in all_values and not key_found:
                    detected_type = "manual key"
                    nullable = False
                    key_found = True

                # Integers:

                elif integer_values == len(data):
                    detected_type = "integer"
                    nullable = False

                elif integer_values > 0 and len(other_values) == 1:
                    detected_type = "integer"
                    nullable = True

                elif integer_values > 0 and len(other_values) > 1 and (integer_values > 100):
                    detected_type = "integer"
                    nullable = True
                    include_alternate = True

                # Decimals: TODO: more

                elif decimal_values > 0 and len(other_values) in (0, 1):
                    # Integer or decimal values -> use a decimal field.
                    # TODO: Find number of digits!!!
                    detected_type = "decimal"
                    nullable = (len(other_values) == 1)
                    max_length = max_seen_length + max_seen_decimals + 4

                # Floats: TODO: more

                elif float_values > 0 and len(other_values) in (0, 1):
                    # Integer, decimal or float values in column -> use a float field.
                    detected_type = "float"
                    nullable = (len(other_values) == 1)

                # Dates:

                elif date_values == len(data):
                    detected_type = "date"
                    nullable = False
                    # TODO: Detect date format and make additional settings with date format

                elif date_values > 0 and len(other_values) == 1:
                    detected_type = "date"
                    nullable = True
                    null_values = list(other_values)[0]

                # Times:

                elif time_values == len(data):
                    detected_type = "time"
                    nullable = False
                    # TODO: Detect time format and make additional settings with time format

                elif time_values > 0 and len(other_values) == 1:
                    detected_type = "time"
                    nullable = True
                    null_values = list(other_values)[0]

                # Enums:

                elif len(all_values) < 10 and integer_values <= 1 and max_seen_length < 24:
                    detected_type = "text"
                    nullable = ("" in all_values)
                    choices = sorted(list([c for c in all_values if c != ""]))
                    max_length = max_seen_length * 2

                    # Booleans:
                    if len(choices) in (2, 3):
                        in_choices = [c.lower() for c in choices]
                        if ("n" in in_choices and "y" in in_choices) or \
                                ("no" in in_choices and "yes" in in_choices) or \
                                ("t" in in_choices and "f" in integer_values) or \
                                ("true" in in_choices and "false" in in_choices):

                            detected_type = "boolean"
                            nullable = (len(choices) == 3)
                            null_values = [c for c in choices
                                           if c.lower() not in ("n", "y", "no", "yes", "t", "f", "true", "false")]

                # Text

                elif integer_values < max(len(data) / 10, 10) or len(other_values) >= 10:
                    detected_type = "text"
                    nullable = False

                design_writer.writerow([
                    f,  # Old field name
                    new_name,  # New field name (in database)
                    detected_type,  # Detected data type
                    str(nullable).lower(),  # Whether the field is nullable
                    "; ".join(null_values),  # What value(s) will become null in the database
                    "",  # The default value for the field (optional, null/blank if left empty)
                    "!fill me in!",  # Field description
                    *[m for m in [max(max_length, 2), max(max_seen_decimals, 1)] if detected_type == "decimal"],
                    *[m for m in [max_length] if detected_type == "text" and max_length > 0],  # IF TEXT/ENUM: max l.
                    *["; ".join([c for c in choices
                                 if len(choices) > 0 and detected_type != "boolean"])],  # IF ENUM: Choices
                ])

                if include_alternate:
                    design_writer.writerow([
                        f,
                        new_name + "_alt",  # New field name (in database; alternate)
                        "text",  # Alternate fields are always text, possibly with choices
                        "false",  # Alt. fields cannot be null
                        "",
                        "",
                        "!fill me in!"
                    ])

                print("Detected type for field '{}': '{}' (nullable: {}{}{})".format(
                    f,
                    detected_type,
                    nullable,
                    ", choices: {}".format(choices) if len(choices) > 0 else "",
                    ", with alternate" if include_alternate else ""
                ))

            design_writer.writerow([])


if __name__ == "__main__":
    main()
