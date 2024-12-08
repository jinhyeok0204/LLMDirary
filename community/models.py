from django.db import models
from accounts.models import Person, User
from django.utils.timezone import now


class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    post_publisher = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, related_name='posts')
    post_write_datetime = models.DateTimeField(auto_now_add=True)
    post_title = models.CharField(max_length=40, default="")
    post_content = models.TextField()
    is_pinned = models.BooleanField(default=False)

    def __str__(self):
        return f"Post by {self.post_publisher.name} on {self.post_write_datetime}"


class PostComment(models.Model):
    post_comment_id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post_comment_write_datetime = models.DateTimeField(auto_now_add=True)
    post_comment_content = models.TextField()

    def __str__(self):
        return f"Comment by {self.user.id.name} on {self.post_comment_write_datetime}"
