from typing import Dict, Optional, Tuple


__all__ = [
    "get_choices_from_text_field",
]


def get_choices_from_text_field(f: Dict) -> Optional[Tuple[str, ...]]:
    if len(f["additional_fields"]) == 2:
        # TODO: Choice human names
        choice_names = tuple(str(c).strip() for c in f["additional_fields"][1].split(";") if str(c).strip() != "")
        return choice_names if len(choice_names) > 0 else None
    return None
