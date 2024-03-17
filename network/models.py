from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    post_message = models.CharField(max_length=300)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post ID {self.id} wrote by {self.author} on {self.date.strftime('%d %b %Y %H:%M:%S')}"
    
class Follower(models.Model):
    followed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed_user")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")

    def __str__(self):
        return f"{self.followed_user} is followed by {self.follower}"
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_like")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_like")

    def __str__(self):
        return f"{self.user} liked {self.post}"
