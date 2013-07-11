from django.contrib import admin
from .models import Vision, Reply, Share, Moment


class ShareInline (admin.TabularInline):
    model = Share
    extra = 1


class ReplyInline (admin.TabularInline):
    model = Reply
    extra = 1


class VisionAdmin (admin.ModelAdmin):
    inlines = [ReplyInline, ShareInline]


admin.site.register(Moment)
admin.site.register(Vision, VisionAdmin)
