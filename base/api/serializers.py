from rest_framework.serializers import ModelSerializer
from base.models import Room


# Take python objects and serialize all its fields into Json objects
class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"
