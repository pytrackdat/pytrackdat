import os
import pathlib
import shutil
import subprocess
import sys

from django.http import FileResponse, JsonResponse

__all__ = [
    "HAVE_R",
    "labels_for_queryset",
    "labels_response",
]


HAVE_R = shutil.which("Rscript") is not None
LABELS_OUT_DIR = pathlib.Path(__file__).parent.parent.resolve() / "tmp"
EXPORT_LABELS_SCRIPT_PATH = pathlib.Path(__file__).parent.parent.parent.resolve() / "util_files" / "export_labels.R"


def labels_for_queryset(model_name, queryset):
    id_vector = [f"{model_name}\n{o.pk}" for o in queryset]

    if not id_vector:
        return None, "No valid objects were found in the database for the provided IDs"

    for f in os.listdir(LABELS_OUT_DIR):
        if f.startswith("labels-"):
            os.remove(LABELS_OUT_DIR / f)

    if HAVE_R:
        # TODO: Prefix for IDs
        result = subprocess.run(
            ["Rscript", str(EXPORT_LABELS_SCRIPT_PATH), str(LABELS_OUT_DIR)] + id_vector,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("export_labels.R results:", result)

        if result.returncode != 0:
            err = f"Error encountered while running export_labels.R script; stdout={result.stdout.decode('utf-8')}; " \
                  f"stderr={result.stderr.decode('utf-8')}"
            print(err, file=sys.stderr)
            return None, err

        path = LABELS_OUT_DIR / (result.stdout.decode("utf-8").split("\n")[-1] + ".pdf")
        return path, None

    return None, "R is not present on the system running PyTrackDat"


def labels_response(model_name, queryset):
    label_path, err = labels_for_queryset(model_name, queryset)

    if label_path is not None:
        # Cannot use `with` statement, since it'll result in the following error:
        #    ValueError: read of closed file
        response = FileResponse(
            open(label_path, "rb"),
            as_attachment=True,
            filename=f"labels_{model_name.lower()}.pdf")
    else:
        response = JsonResponse({"error": str(err)}, status=500)

    return response
