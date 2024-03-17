import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q, BooleanField, OuterRef, Subquery
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Follower, Like

from django.core.serializers import serialize


def index(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            all_posts = Post.objects.prefetch_related('post_like')
            all_posts = all_posts.order_by('-date')
            data = serialize('json', all_posts, fields=('id', 'post_message', 'author'))
            # print(data.post_message)
            # print(data)
            print(1)
            # add is_liked column
            all_posts = all_posts.annotate(
                is_liked=Subquery(
                    Like.objects.filter(user=request.user, post=OuterRef('pk')).values('pk')[:1],
                    output_field=BooleanField()
            ))
        else:
            all_posts = Post.objects.all().order_by('-date')

        # Paginator
        paginator = Paginator(object_list=all_posts, per_page=10)
        page_number = request.GET.get('page')
        page_objects = paginator.get_page(page_number)

        context = {
            "page_name": "index",
            "page_objects": page_objects,
        }
        return render(request, "network/index.html", context)
    
    else:
        return HttpResponseBadRequest("Bad request")
    
@login_required
@csrf_exempt
def edit_post(request):
    if request.method == "PUT":
        current_user = request.user
        data = json.loads(request.body)
        post_id = data.get("post_id", "")
        post_message = data.get("post_message", "")
        print(post_message, post_id)
        
        try:
            post = Post.objects.get(author=current_user, pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)

        post.post_message = post_message
        post.save()
        return HttpResponse(status=204)
    else:
        return HttpResponseBadRequest("Bad request")
    
@login_required
@csrf_exempt
def toggle_like(request):
    if request.method == "POST":
        current_user = request.user
        data = json.loads(request.body)
        post_id = data.get("post_id", "")
        post = Post.objects.get(pk=post_id)
        is_liked = Like.objects.filter(post=post, user=current_user)

        if is_liked:
            like_action = "unlike"
            is_liked.delete()
            
        else:
            like_action = "like"
            new_like = Like(post=post, user=current_user)
            new_like.save()

        likes_count = Like.objects.filter(post=post).count()

        context = {
            "likes_count": likes_count,
            "like_action": like_action,
        }
    
        return JsonResponse(context, status=200, safe=False)
    else:
        return HttpResponseBadRequest("Bad request")
    

@login_required
def new_post(request):
    if request.method == "POST":
        current_user = request.user
        post_message = request.POST["post_message"]

        post = Post(post_message=post_message, author=current_user) # date is auto_now_add
        post.save()
        
        return HttpResponseRedirect(reverse("index"))
    else:
        return HttpResponseBadRequest("Bad request")
    
def view_profile(request, user_id):
    current_user = request.user
    try:
        viewed_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    
    if current_user.is_authenticated:
        all_posts = Post.objects.prefetch_related('post_like')
        all_posts = all_posts.filter(author=viewed_user).order_by('-date')
        # add is_liked column
        all_posts = all_posts.annotate(
            is_liked=Subquery(
                Like.objects.filter(user=request.user, post=OuterRef('pk')).values('pk')[:1],
                output_field=BooleanField()
        ))

    else:
        all_posts = Post.objects.filter(author=viewed_user).order_by('-date')
        check_follow = None

    # follower
    following = Follower.objects.filter(follower=viewed_user)
    follower = Follower.objects.filter(followed_user=viewed_user)
    if current_user.is_authenticated:
        check_follow = follower.filter(follower=current_user)
    
    if check_follow:
        is_following = True
    else:
        is_following = False

    # Paginator
    paginator = Paginator(object_list=all_posts, per_page=10)
    page_number = request.GET.get('page')
    page_objects = paginator.get_page(page_number)

    context = {
        "page_name": "view_profile",
        "viewed_user": viewed_user,
        "page_objects": page_objects,
        "following": following,
        "follower": follower,
        "is_following": is_following,
    }
    return render(request, "network/index.html", context)

@login_required
@csrf_exempt
def toggle_follow(request):
    if request.method == "POST":
        current_user = request.user
        data = json.loads(request.body)
        follow_action = data.get("follow_action", "")
        followed_user_id = data.get("followed_user_id", "")
        followed_user = User.objects.get(pk=followed_user_id)

        if follow_action == "Follow":
            new_follow = Follower(followed_user=followed_user, follower=current_user)
            new_follow.save()
        else:
            unfollow = Follower.objects.get(followed_user=followed_user, follower=current_user)
            unfollow.delete()

        following_count = Follower.objects.filter(follower=followed_user).count()
        follower_count = Follower.objects.filter(followed_user=followed_user).count()

        context = {
            "following_count": following_count,
            "follower_count": follower_count,
        }
    
        return JsonResponse(context, status=200, safe=False)
    else:
        return HttpResponseBadRequest("Bad request")

@login_required
def view_following(request):
    if request.method == "GET":
        current_user = request.user
        following = Follower.objects.filter(follower=current_user)
        following = following.values_list("followed_user")
        all_posts = Post.objects.prefetch_related('post_like')
        # add is_liked column
        all_posts = all_posts.annotate(
            is_liked=Subquery(
                Like.objects.filter(user=request.user, post=OuterRef('pk')).values('pk')[:1],
                output_field=BooleanField()
        ))
        # show only following user
        all_posts = all_posts.filter(author__in=following).order_by('-date')
        # show following user and current user
        # all_posts = Post.objects.filter(Q(author__in=following) | Q(author=current_user)).order_by('-date')

        # Paginator
        paginator = Paginator(object_list=all_posts, per_page=10)
        page_number = request.GET.get('page')
        page_objects = paginator.get_page(page_number)

        context = {
            "page_name": "Following",
            "page_objects": page_objects,
        }
        return render(request, "network/index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
