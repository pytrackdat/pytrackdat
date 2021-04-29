import csv
import re

# TODO: py3.9: Change these to new type hints
from typing import IO, List

from pytrackdat import common as c
from . import formatters
from .errors import DesignFileError
from .utils import get_default_from_csv_with_type

# TODO: TIMEZONES
# TODO: Multiple date formats
# TODO: More ways for custom validation
# TODO: More customization options


def design_to_relations(df: IO, gis_mode: bool) -> List[c.Relation]:
    """
    Validates the design file and converts it into relations and their fields.
    """

    relations = []

    design_reader = csv.reader(df)
    relation_name_and_headers = next(design_reader)

    end_loop = False

    while not end_loop:
        design_relation_name = relation_name_and_headers[0]

        relation_fields = []
        id_type = ""

        end_inner_loop = False

        while not end_inner_loop:
            try:
                current_field = next(design_reader)
                while current_field and "".join(current_field).strip() != "":
                    # TODO: Process

                    field_name = c.field_to_py_code(current_field[1])
                    data_type = c.standardize_data_type(current_field[2])

                    if not c.valid_data_type(data_type, gis_mode):
                        raise DesignFileError(
                            f"Error: Unknown data type specified for field '{field_name}': '{data_type}'.")

                    nullable = current_field[3].strip().lower() in c.BOOLEAN_TRUE_VALUES
                    # TODO: Covert to correct type?
                    null_values = tuple([n.strip() for n in current_field[4].split(";")])

                    if data_type in c.KEY_TYPES and id_type != "":
                        raise DesignFileError(
                            "Error: More than one primary key (auto/manual key) was specified for relation '{}'. "
                            "Please only specify one primary key.".format(design_relation_name)
                        )

                    if data_type == c.DT_AUTO_KEY:
                        id_type = "integer"  # TODO: DT_ ?
                    elif data_type == c.DT_MANUAL_KEY:
                        id_type = "text"  # TODO: DT_ ?

                    csv_names = tuple(re.split(r";\s*", current_field[0]))
                    # TODO: Specify more permissible data types here
                    if len(csv_names) > 1 and data_type not in (c.DT_GIS_POINT,):
                        # TODO: Codify this better
                        raise DesignFileError(
                            f"Error: Cannot take more than one column as input for field '{current_field[0]}' with "
                            f"data type {data_type}.")

                    # TODO: Have blank mean a default inference instead of False
                    show_in_table = current_field[7].strip().lower() in c.BOOLEAN_TRUE_VALUES
                    if data_type in c.KEY_TYPES and not show_in_table:
                        print(f"Warning: Primary key '{field_name}' must be shown in table; overriding false-like "
                              f"value...")
                        show_in_table = True

                    default_str = current_field[5].strip()
                    default = get_default_from_csv_with_type(field_name, default_str, data_type, nullable, null_values)

                    # TODO: This handling of additional_fields could eventually cause trouble, because it can shift
                    #  positions of additional fields if a blank additional field occurs before a valued one.
                    current_field_obj = c.RelationField(
                        csv_names=csv_names,
                        name=field_name,
                        data_type=data_type,
                        nullable=nullable,
                        null_values=null_values,
                        default=default,
                        description=current_field[6].strip(),
                        show_in_table=show_in_table,
                        additional_fields=tuple(f for f in current_field[8:] if f.strip() != "")
                    )

                    if (len(current_field_obj.additional_fields) >
                            len(c.DATA_TYPE_ADDITIONAL_DESIGN_SETTINGS[data_type])):
                        if data_type in c.KEY_TYPES and len(current_field_obj.additional_fields) == 2 and \
                                c.DESIGN_SEPARATOR in current_field_obj.additional_fields[1]:
                            # Looks like user tried to specify choices for a key-type
                            # TODO: This is heuristic-based, and should be re-examined if additional_fields changes
                            #  for the key types.
                            c.exit_with_error(
                                "Error: Choices aren't valid for a primary key (auto or manual.) If this was\n"
                                "       specifiable, there could only be as many rows as choices, and the choices\n"
                                "       would not be modifiable after the database is constructed."
                            )

                        else:
                            print(
                                "Warning: More additional settings specified for field '{field}' than can be used.\n"
                                "         Available settings: '{settings}' \n".format(
                                    field=field_name,
                                    settings="', '".join(c.DATA_TYPE_ADDITIONAL_DESIGN_SETTINGS[data_type])
                                )
                            )

                    if data_type == c.DT_TEXT:
                        choices = formatters.get_choices_from_text_field(current_field_obj)
                        if choices is not None and default_str != "" and default_str not in choices:
                            raise DesignFileError(
                                "Error: Default value for field '{field}' in relation '{relation}' does not match \n"
                                "       any available choices for the field. \n"
                                "       Available choices: {choices}".format(
                                    field=current_field[1],
                                    relation=design_relation_name,
                                    choices=", ".join(choices)
                                ))

                        current_field_obj.choices = choices if choices is not None and len(choices) > 1 else None

                    relation_fields.append(current_field_obj)

                    current_field = next(design_reader)

            except StopIteration:
                if len(relation_fields) == 0:
                    end_loop = True
                    break

            # Otherwise, save the relation information.
            relations.append(c.Relation(design_name=design_relation_name, fields=relation_fields, id_type=id_type))

            # Find the next relation.

            relation_name_and_headers = ()

            try:
                while "".join(relation_name_and_headers).strip() == "":
                    rel = next(design_reader)
                    if len(rel) > 0:
                        relation_name_and_headers = rel
                        end_inner_loop = True

            except StopIteration:
                end_loop = True
                break

    return relations
