from django.shortcuts import redirect, render
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.forms import UserCreationForm


# create user login
def loginPage(request):
    page = "login"
    # If user is already login, they will return to home when try loging in again through url
    if request.user.is_authenticated:
        return redirect("home")

    # get inputed username and password
    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")

        # check if the inputed user exist, otherwise throw out a flash error
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")

        # Use username and password to authenticate, then login the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username or Password does not exist")
    context = {"page": page}
    return render(request, "base/login_register.html", context)


# create logout user
def logoutUser(request):
    logout(request)
    return redirect("home")


# register user
def registerPage(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error occured during registeration")

    context = {"form": form}
    return render(request, "base/login_register.html", context)


# go to home page
def home(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    # dynamics search
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    # count the number of rooms
    total_room = Room.objects.all().count()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages,
        "total_room": total_room,
    }
    return render(request, "base/home.html", context)


# go to a selected room
def room(request, pk):
    room = Room.objects.get(id=pk)
    # get every messages related to the room
    room_message = room.message_set.all().order_by("-created")
    participants = room.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user=request.user, room=room, body=request.POST.get("comment")
        )
        # add new participants when they messaged in the room
        room.participants.add(request.user)
        return redirect("room", pk)

    context = {"room": room, "room_message": room_message, "participants": participants}
    return render(request, "base/room.html", context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    total_room = Room.objects.all().count()
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        "user": user,
        "rooms": rooms,
        "room_messages": room_messages,
        "topics": topics,
        "total_room": total_room,
    }
    return render(request, "base/profile.html", context)
  

# restrict user if not authenticated
@login_required(login_url="login")
# create a room
def createroom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        return redirect("home")

    context = {"form": form, "topics": topics}
    return render(request, "base/room-form.html", context)


# restrict user if not authenticated
@login_required(login_url="login")
# update a room
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    # if user is not the host, restrict their access
    if request.user != room.host:
        return HttpResponse("YOU ARE NOT ALLOWED HERE!!!")

    if request.method == "POST":
        # get the topic name from user input
        topic_name = request.POST.get("topic")
        # either get the inputed topic, or create one if it does not exist
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()
        return redirect("home")

    context = {"form": form, "topics": topics, "room": room}
    return render(request, "base/room-form.html", context)


# Restrict user if not authenticated
login_required(login_url="login")


# delete a room
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    # if user is not the host, restrict their access
    if request.user != room.host:
        return HttpResponse("YOU ARE NOT ALLOWED HERE!!!")
    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": room})


# delete a message
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    # if user is not the message user, restrict their access
    if request.user != message.user:
        return HttpResponse("YOU ARE NOT ALLOWED DO SO!!!")
    if request.method == "POST":
        message.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": message})


@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)

    context = {"form": form}
    return render(request, "base/update-user.html", context)


def topicsPage(request):
    total_room = Room.objects.all().count()

    q = request.GET.get("q") if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(name__icontains=q)

    context = {"topics": topics, "total_room": total_room}
    return render(request, "base/topics.html", context)


def activityPage(request):
    room_message = Message.objects.all()

    context = {"room_message": room_message}
    return render(request, "base/activity.html", context)



