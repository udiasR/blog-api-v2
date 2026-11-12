from django.db import models
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateTimeField,
    ForeignKey,
    ManyToManyField,
    SlugField,
    TextChoices,
    TextField,
)

from settings import base


# Create your models here.
class Category(models.Model):
    name = CharField(max_length=100, unique=True)   
    slug = SlugField(unique=True)
    
    class Meta: 
        verbose_name_plural = "categories"

    def __str__(self): 
        return self.name

class Tag(models.Model):
    name = CharField(max_length=50, unique=True)   
    slug = SlugField(unique=True)
    class Meta: 
        verbose_name_plural = "categories"
    
    
    def __str__(self): 
        return self.name

class Post(models.Model):
    class Status(TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
    author = ForeignKey(base.AUTH_USER_MODEL, on_delete=CASCADE, related_name="posts")
    title = CharField(max_length=200)
    slug = SlugField(unique=True)
    body = TextField()
    category = ForeignKey(Category, on_delete=SET_NULL, null=True, blank=True, related_name="posts")
    tags = ManyToManyField(Tag, blank=True, related_name="posts")
    status = CharField(max_length=10, choices=Status, default=Status.DRAFT)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

class Comment(models.Model):
    post = ForeignKey(Post, on_delete=CASCADE, related_name="comments")
    author = ForeignKey(base.AUTH_USER_MODEL, on_delete=CASCADE, related_name="comments")
    body = TextField()
    created_at = DateTimeField(auto_now_add=True)
