from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer


# Show the available routes for the api
@api_view(["GET"])
def getRoutes(request):
    routes = [
        "GET /api",
        "GET /api/rooms",
        "GET /api/rooms/:id",
    ]
    # Return routes
    return Response(routes)


@api_view(["GET"])
def getRooms(request):
    rooms = Room.objects.all()
    # Serialize python object "rooms" that has many objects
    serializer = RoomSerializer(rooms, many=True)
    # return serialized data
    return Response(serializer.data)


@api_view(["GET"])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    # Serialize one specific python object
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)
