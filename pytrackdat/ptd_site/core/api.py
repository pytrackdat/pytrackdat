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
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from typing import List

from pytrackdat.common import PDT_RELATION_PREFIX, API_FILTERABLE_FIELD_TYPES, Relation
from pytrackdat.ptd_site.core import models as core_models
from pytrackdat.ptd_site.snapshot_manager.models import Snapshot

__all__ = ["api_router"]


api_router = DefaultRouter()


relations: List[Relation] = []

for name in dir(core_models):
    Cls = getattr(core_models, name)
    if not name.startswith(PDT_RELATION_PREFIX) or type(Cls) != models.base.ModelBase:
        continue

    # noinspection PyUnresolvedReferences
    relation: Relation = Cls.ptd_relation
    relations.append(relation)
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


api_router.register("snapshots", SnapshotViewSet)
api_router.register("meta", MetaViewSet, basename="meta")
