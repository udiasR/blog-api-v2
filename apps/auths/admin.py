
# Register your models here.
from django.contrib.admin import register
from unfold.admin import ModelAdmin
from apps.auths.models import CustomUser, CustomUserManager
from django.contrib.auth.models import Group
from django.contrib import admin

admin.site.unregister(Group)

@register(Group)
class GroupAdmin(ModelAdmin):
    search_fields = ("name",)
    filter_horizontal = ("permissions",)




@register(CustomUser)
class CustomUserAdmin(ModelAdmin):
    """
    CustomUser model admin configuration class.
    """

    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "is_active",
        # "is_deleted",          # not a field, a method (see below)
    )
    list_display_links = (
        "id",
        "email",
    )
    list_filter = (
        "is_staff",
        "is_active",
        # IsDeletedListFilter,   # our own filter (§6)
    )
    search_fields = (
        "id",
        "email",
    )
    
    list_per_page = 50


