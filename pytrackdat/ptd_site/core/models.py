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

import sys

from django.conf import settings
from django.db import models

from pytrackdat.design_file import design_to_relations
from pytrackdat.generation.formatters import DJANGO_TYPE_FORMATTERS


all_exports = []


with open(settings.PTD_DESIGN_FILE, "r") as df:
    relations = design_to_relations(df, settings.PTD_GIS_MODE)
    for r in relations:
        Model = type(r.name, (models.Model,), {
            **{
                f.name: DJANGO_TYPE_FORMATTERS[f.data_type](f)
                for f in r.fields
            },
            "ptd_relation": r,
            "__str__": classmethod(lambda self: f"{r.short_name}: {self.pk}"),
            "Meta": type("Meta", (object,), {"verbose_name": r.short_name}),
            "__module__": __name__,
        })
        setattr(sys.modules[__name__], r.name, Model)
        all_exports.append(r.name)


__all__ = all_exports
