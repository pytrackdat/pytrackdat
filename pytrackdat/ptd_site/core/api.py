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
import re
import sys

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.functions import Cast
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from collections.abc import Iterable
from typing import Dict, List, Optional, Tuple

from pytrackdat.common import DT_TEXT, PDT_RELATION_PREFIX, API_FILTERABLE_FIELD_TYPES, SEARCHABLE_FIELD_TYPES, Relation
from pytrackdat.ptd_site.core import models as core_models
from pytrackdat.ptd_site.snapshot_manager.models import Snapshot

__all__ = ["api_router"]


api_router = DefaultRouter()


relations: List[Relation] = []
model_dict: Dict[str, models.Model] = {}

for name in dir(core_models):
    Cls = getattr(core_models, name)
    if not name.startswith(PDT_RELATION_PREFIX) or type(Cls) != models.base.ModelBase:
        continue

    # noinspection PyUnresolvedReferences
    relation: Relation = Cls.ptd_relation
    relations.append(relation)
    model_dict[Cls.ptd_relation.short_name.lower()] = Cls
    # TODO: Abstract mixin for this stuff

    serializer_name = f"{name}Serializer"
    NewSerializerMeta = type("Meta", (object,), {"model": Cls, "fields": "__all__"})
    NewSerializer = type(f"{name}Serializer", (serializers.ModelSerializer,), {"Meta": NewSerializerMeta})

    # This MUST be called categorical_counts to match the attribute name on the viewset class
    def categorical_counts(_self, _request):
        categorical_fields = tuple(f.name for f in relation.fields if f.choices is not None)
        categorical_choices = {
            f.name: f.choices + (("",) if f.nullable else ())
            for f in relation.fields if f.choices is not None
        }
        counts = {f: {c: 0 for c in categorical_choices[f]} for f in categorical_fields}
        for row in Cls.objects.values():
            for f in categorical_fields:
                counts[f][row[f]] += 1
        return Response(counts)

    viewset_name = f"{name}ViewSet"
    NewViewSet = type(viewset_name, (viewsets.ModelViewSet,), {
        "queryset": Cls.objects.all(),
        "serializer_class": NewSerializer,
        "filterset_fields": {
            f.name: API_FILTERABLE_FIELD_TYPES[f.data_type]
            for f in relation.fields if f.data_type in API_FILTERABLE_FIELD_TYPES
        },
        "categorical_counts": action(detail=False)(categorical_counts)
    })

    setattr(sys.modules[__name__], serializer_name, NewSerializer)
    setattr(sys.modules[__name__], viewset_name, NewViewSet)

    api_router.register(f"data/{relation.name_lower}", NewViewSet)

model_name_set = set(n for n in model_dict)


# TODO: Maybe put this in the snapshot app...
class SnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snapshot
        fields = "__all__"


# TODO: Maybe put this in the snapshot app...
class SnapshotViewSet(viewsets.ModelViewSet):
    queryset = Snapshot.objects.all()
    serializer_class = SnapshotSerializer


# noinspection PyMethodMayBeStatic
class MetaViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        return Response({
            "site_name": settings.PTD_SITE_NAME,
            "gis_mode": settings.PTD_GIS_MODE,
            # TODO: Filter relations by permission of individual
            **({"relations": [dict(r) for r in relations]} if request.user and not request.user.is_anonymous else {}),
        })


def _get_model_search_fields(model: models.Model) -> List[Tuple[str, Optional[str]]]:
    model_search_fields = []

    for f in model.ptd_relation.fields:
        if f.data_type not in SEARCHABLE_FIELD_TYPES:
            continue

        if f.data_type == DT_TEXT:
            model_search_fields.append((f.name, None))
        else:
            model_search_fields.append((f.name, f"{f.name}_str"))

    return model_search_fields


def _get_field_searchable(f: Tuple[str, Optional[str]]):
    return f"{f[1] if f[1] is not None else f[0]}__icontains"


# noinspection PyUnresolvedReferences
def search_model(
        query: str,
        model: models.Model,
        limit: int = 50,
        fields: Iterable[Tuple[str, Optional[str]]] = (("pk", "pk_str"),),
):
    model_name = model.ptd_relation.short_name
    model_url_name = model.ptd_relation.name_lower

    db_q = Q(**{_get_field_searchable(fields[0]): query})

    for f in fields[1:]:
        db_q = db_q | Q(**{_get_field_searchable(f): query})

    to_annotate = {k[1]: Cast(k[0], output_field=models.CharField()) for k in fields if k[1] is not None}

    queryset = model.objects
    if to_annotate:
        queryset = queryset.annotate(**to_annotate)

    return [{
        "name": model_name,
        "url_name": model_url_name,
        "pk": res.pk,
        "matching_fields": [
            {kk: r}
            for kk, r in ((k[0], str(getattr(res, k[0]))) for k in fields)
            if query.casefold() in r.casefold()
        ],
    } for res in queryset.filter(db_q)[:limit]]


# noinspection PyMethodMayBeStatic
class SearchViewSet(viewsets.ViewSet):
    def list(self, request):
        query: Optional[str] = request.query_params.get("q")

        try:
            limit = int(request.query_params.get("limit", "50"))
        except ValueError:
            raise ValidationError(detail="limit must be an integer")

        if limit < len(model_name_set) or limit > 100:
            raise ValidationError(detail=f"limit must be between {len(model_name_set)} and 100")

        if query is None:
            raise ValidationError(detail="q parameter must be specified")

        split = re.split(r"\s+", query)
        results = {
            "barcodes": [],
            "full_text": [],  # If left as None, full text search is not available
        }

        if len(split) == 2 and split[0].lower() in model_name_set:
            # Treat this as a barcode and try to fetch partial or whole matches
            # These will be the "first response" matches, before partial matches are considered further

            m = model_dict[split[0].lower()]
            results["barcodes"].extend(search_model(split[1], m, limit))

        else:
            # Pretty limited for now: search a few fields on all models
            for n, m in model_dict.items():
                results["full_text"].extend(search_model(
                    query,
                    m,
                    limit=limit // len(model_name_set),
                    fields=_get_model_search_fields(m)))

        # TODO: If Postgres is present, use their engine to full-text-search all the models
        #  and maybe rank them somehow...

        return Response(results)


api_router.register("snapshots", SnapshotViewSet)
api_router.register("meta", MetaViewSet, basename="meta")
api_router.register("search", SearchViewSet, basename="search")
