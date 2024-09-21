from rest_framework import viewsets

from config.utils_methods import create_instance, list_all_objects, update_instance
from .models import FieldType, CustomField, CustomFieldOption, CustomFieldValue, Entities
from .serializers import FieldTypeSerializer, CustomFieldSerializer, CustomFieldOptionSerializer, CustomFieldValueSerializer, EntitiesSerializer


class FieldTypeViewSet(viewsets.ModelViewSet):
    queryset = FieldType.objects.all()
    serializer_class = FieldTypeSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)    


class CustomFieldViewSet(viewsets.ModelViewSet):
    queryset = CustomField.objects.all()
    serializer_class = CustomFieldSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class CustomFieldOptionViewSet(viewsets.ModelViewSet):
    queryset = CustomFieldOption.objects.all()
    serializer_class = CustomFieldOptionSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class EntitiesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Entity model.
    """
    queryset = Entities.objects.all()
    serializer_class = EntitiesSerializer

class CustomFieldValueViewSet(viewsets.ModelViewSet):
    queryset = CustomFieldValue.objects.all()
    serializer_class = CustomFieldValueSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

# class CustomFieldEntityMappingViewSet(viewsets.ModelViewSet):
#     queryset = CustomFieldEntityMapping.objects.all()
#     serializer_class = CustomFieldEntityMappingSerializer

#     def list(self, request, *args, **kwargs):
#         return list_all_objects(self, request, *args, **kwargs)

#     def create(self, request, *args, **kwargs):
#         return create_instance(self, request, *args, **kwargs)

#     def update(self, request, *args, **kwargs):
#         return update_instance(self, request, *args, **kwargs)