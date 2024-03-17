from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # watchlist
    pass

class Category(models.Model):
    category_name = models.CharField(max_length=64)

    def __str__(self):
        return self.category_name
    
    
# listings(title, description, starting bids, active status, optional add category or image)  #users can create new
class Listing(models.Model):
    # need to fill when create
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=300)
    image_url = models.CharField(max_length=500)
    currency = models.CharField(max_length=3, default="THB")
    starting_bid = models.FloatField()
    category = models.ManyToManyField(Category, blank=True, related_name="category")
    #optional
    close_date = models.DateField(blank=True, null=True, default=None)
    # auto fill value
    price = models.FloatField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user") # if user is deleted, the list will be deleted.
    watchlist_user = models.ManyToManyField(User, blank=True, null=True, related_name="watchlist_user")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="winner")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
class Bid(models.Model):
    bid = models.FloatField(default=0)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid_listing")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.bid
    
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="commented_listing")
    comment_message = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} comment on listing: {self.listing}"
    


    



# bids
# comments made on auction listings
# listing category
