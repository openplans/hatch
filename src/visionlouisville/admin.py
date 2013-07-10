from django.contrib import admin
from .models import Vision, Reply


class ReplyInline (admin.TabularInline):
    model = Reply
    extra = 1


class VisionAdmin (admin.ModelAdmin):
    inlines = [ReplyInline]


admin.site.register(Vision, VisionAdmin)
