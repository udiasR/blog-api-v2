
# Register your models here.
from django.contrib.admin import ModelAdmin, register
from apps.auths.models import CustomUser, CustomUserManager


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


