from django.contrib import admin
from .models import Vision, Reply, Support


class ReplyInline (admin.TabularInline):
    model = Reply
    extra = 1


class VisionAdmin (admin.ModelAdmin):
    inlines = [ReplyInline]

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        # HACK: Django admin wants to hide the multiselect widget because
        #       we're using a through model.
        if db_field.name == 'supporters':
            db_field.rel.through._meta.auto_created = True

        return super(VisionAdmin, self).formfield_for_manytomany(
            db_field, request, **kwargs)


admin.site.register(Vision, VisionAdmin)
