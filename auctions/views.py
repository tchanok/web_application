from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import date, timedelta

from .models import User, Category, Listing, Comment, Bid


def index(request):
    create_all_category()
    close_auctions_by_date()
    active_listing = Listing.objects.filter(is_active=True)
    all_categories = Category.objects.all()
    selected_category = Category.objects.get(category_name="All")

    return render(request, "auctions/index.html",{
        "listings": active_listing,
        "categories": all_categories,
        "selected_category": selected_category,
    })

def close_auctions_by_date():
    today_date = date.today()
    # filter active listings that has close date before or equal today
    close_listings = Listing.objects.filter(is_active=True, close_date__lte=today_date)
    if close_listings:
        for listing in close_listings:
            listing.is_active = False
            last_bid = Bid.objects.order_by('-created_at').first()
            listing.winner = last_bid.bidder
            listing.save()

def create_all_category():
    # create 'All' category
    all_category = Category.objects.filter(category_name="All")
    if not all_category:
        all_category = Category(category_name="All")
        all_category.save()

def my_listing(request):
    if request.user.is_authenticated:
        current_user = request.user
        my_listings = Listing.objects.filter(owner=current_user)
        all_categories = Category.objects.all()
        return render(request, "auctions/my_watchlist.html",{
            "page_title": "My Listings",
            "listings": my_listings,
            "categories": all_categories,
        })
    else:
        return HttpResponseRedirect(reverse("login"))

def bidded_listing(request):
    if request.user.is_authenticated:
        current_user = request.user
        my_bids = Bid.objects.filter(bidder=current_user)
        unique_listings_pk = get_unique_listings_from_my_bids(my_bids)
        bidded_listings = Listing.objects.filter(id__in=unique_listings_pk)
        all_categories = Category.objects.all()
        return render(request, "auctions/my_watchlist.html",{
            "page_title": "Bidded Listings",
            "listings": bidded_listings,
            "categories": all_categories,
        })
    else:
        return HttpResponseRedirect(reverse("login"))

def get_unique_listings_from_my_bids(my_bids):
    unique_listings_pk = []
    for bid in my_bids:
        pk = bid.listing.id
        if pk not in unique_listings_pk:
            unique_listings_pk.append(pk)
    return unique_listings_pk

def display_category(request):
    if request.method == "POST":
        # get QuerySet of selected category
        selected_category_query = request.POST["category"] 
        # get __str__ of category model
        selected_category = Category.objects.get(category_name=selected_category_query)
        filter_listings = Listing.objects.filter(is_active=True, category=selected_category)
        all_categories = Category.objects.all()
        return render(request, "auctions/index.html",{
            "listings": filter_listings,
            "categories": all_categories,
            "selected_category": selected_category,
        })
    
def listing_page(request, listing_id):
    if request.user.is_authenticated:
        listing_data = Listing.objects.get(pk=listing_id)
        is_watchlist = request.user in listing_data.watchlist_user.all()
        all_comments = Comment.objects.filter(listing=listing_data).order_by('-created_at')
        all_bids = Bid.objects.filter(listing=listing_data).order_by('-created_at')

        return render(request, "auctions/listing_page.html",{
            "listing": listing_data,
            "is_watchlist": is_watchlist,
            "all_comments": all_comments,
            "all_bids": all_bids,
        })
    else:
        return HttpResponseRedirect(reverse("login"))

def add_comment(request, listing_id):
    if request.user.is_authenticated:
        current_user = request.user
        listing_data = Listing.objects.get(pk=listing_id)
        message = request.POST["new_comment"]

        new_comment = Comment(
            author=current_user,
            listing=listing_data,
            comment_message=message
        )
        new_comment.save()

        return HttpResponseRedirect(reverse("listing_page", kwargs={
            "listing_id": listing_id
            }))
    else:
        return HttpResponseRedirect(reverse("login"))

def remove_watchlist(request, listing_id):
    if request.user.is_authenticated:
        listing_data = Listing.objects.get(pk=listing_id)
        current_user = request.user
        listing_data.watchlist_user.remove(current_user)
        return HttpResponseRedirect(reverse("listing_page", kwargs={
            "listing_id": listing_id
            }))
    else:
        return HttpResponseRedirect(reverse("login"))

def add_watchlist(request, listing_id):
    if request.user.is_authenticated:
        listing_data = Listing.objects.get(pk=listing_id)
        current_user = request.user
        listing_data.watchlist_user.add(current_user)
        return HttpResponseRedirect(reverse("listing_page", kwargs={
            "listing_id": listing_id
            }))
    else:
        return HttpResponseRedirect(reverse("login"))

def add_bid(request, listing_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            bid_value = request.POST["new_bid"]
            listing_data = Listing.objects.get(pk=listing_id)
            current_user = request.user
            if float(bid_value) > float(listing_data.price):
                new_bid = Bid(
                    bid=bid_value,
                    bidder=current_user,
                    listing=listing_data,
                )
                new_bid.save()

                listing_data.price = float(bid_value)
                listing_data.save()

                return HttpResponseRedirect(reverse("listing_page", kwargs={
                "listing_id": listing_id
                }))
    else:
        return HttpResponseRedirect(reverse("login"))
        
def close_bid(request, listing_id):
    current_user = request.user
    if request.method == "POST":
        if current_user.is_authenticated:
            listing_data = Listing.objects.get(pk=listing_id)
            if current_user == listing_data.owner:
                listing_data.is_active = False
                last_bid = Bid.objects.order_by('-created_at').first()
                listing_data.winner = last_bid.bidder
                listing_data.save()
                return HttpResponseRedirect(reverse("listing_page", kwargs={
                    "listing_id": listing_id
                    }))
            else:
                HttpResponse(status=403)
        else:
            return HttpResponseRedirect(reverse("login"))
    else:
        return HttpResponse(status=405)
        
def display_watchlist(request):
    if request.user.is_authenticated:
        current_user = request.user
        # get user's watchlist from related name
        my_watchlist = current_user.watchlist_user.all()
        return render(request, "auctions/my_watchlist.html",{
                "page_title": "My Watchlists",
                "listings": my_watchlist,
            })
    else:
        return HttpResponseRedirect(reverse("login"))

def create_listing(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            # show create listing page
            all_categories = Category.objects.all()
            tomorrow = str(date.today() + timedelta(days=1))
            return render(request, "auctions/create_listing.html",{
                "categories": all_categories,
                "tomorrow": tomorrow
            })
        elif request.method == "POST":
            # save new listing and redirect to index page
            # get the data
            title = request.POST["title"]
            description = request.POST["description"]
            image_url = request.POST["image_url"]
            starting_bid = request.POST["starting_bid"]
            currency = request.POST["currency"]
            category = request.POST["category"]
            close_date = request.POST["close_date"]
            if not close_date:
                close_date = None

            # get the category data
            category_data = Category.objects.get(category_name=category)

            # get current user
            current_user = request.user

            # create new object
            new_listing = Listing.objects.create(
                title=title,
                description=description,
                image_url=image_url,
                starting_bid=starting_bid,
                price=starting_bid,
                owner=current_user,
                currency=currency,
                close_date=close_date,
                )
            
            #set up category
            new_listing.category.add(category_data)
            all_category = Category.objects.get(category_name="All")
            new_listing.category.add(all_category)
            new_listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        return HttpResponseRedirect(reverse("login"))


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
