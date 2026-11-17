
# Register your models here.

from django.contrib.admin import register, ModelAdmin
from apps.blog.models import Category, Tag, Post, Comment

@register(Category)
class CategoryAdmin(ModelAdmin):
    """
    Category admin class configuration.
    """

    ...


@register(Tag)
class TagAdmin(ModelAdmin):
    """
    Tag admin class configuration.
    """
    
    ...

@register(Post)
class PostAdmin(ModelAdmin):
    """
    Post admin class configuration.
    """
        
    ...

@register(Comment)
class CommentAdmin(ModelAdmin):
    """
    Comment admin class configuration.
    """
        
    ...