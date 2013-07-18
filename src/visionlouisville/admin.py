from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Vision, Reply, Share, Moment, User


class ShareInline (admin.TabularInline):
    model = Share
    extra = 1


class ReplyInline (admin.TabularInline):
    model = Reply
    extra = 1


class VisionAdmin (admin.ModelAdmin):
    inlines = [ReplyInline, ShareInline]
    # date_hierarchy = 'created_at'
    list_display = ('__unicode__', 'author', 'category', 'updated_at')
    list_filter = ('category', 'created_at', 'updated_at')
    search_fields = ('title', 'details', 'category')


class UserAdmin (BaseUserAdmin):
    list_display = BaseUserAdmin.list_display + ('date_joined', 'visible_on_home',)
    list_editable = BaseUserAdmin.list_editable + ('visible_on_home',)


admin.site.register(Moment)
admin.site.register(Vision, VisionAdmin)
admin.site.register(User, UserAdmin)