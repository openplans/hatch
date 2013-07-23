from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import (
    UserCreationForm as BaseUserCreationForm,
    UserChangeForm as BaseUserChangeForm,
)
from .models import Vision, Reply, Share, Moment, User
from .views import VisionViewSet


class ShareInline (admin.TabularInline):
    model = Share
    extra = 1


class ReplyInline (admin.TabularInline):
    model = Reply
    extra = 3


class VisionAdmin (admin.ModelAdmin):
    inlines = [ReplyInline, ShareInline]
    # date_hierarchy = 'created_at'
    filter_horizontal = ('supporters',)
    list_display = ('__unicode__', 'author', 'category', 'featured', 'created_at', 'updated_at')
    list_editable = ('featured',)
    list_filter = ('category', 'created_at', 'updated_at')
    readonly_fields = ('tweet_text',)
    search_fields = ('text', 'category')

    def change_view(self, request, *args, **kwargs):
        # Save the request so that we can use it when
        # constructing the tweet text.
        self.request = request
        return super(VisionAdmin, self).change_view(request, *args, **kwargs)

    def tweet_text(self, vision):
        return VisionViewSet.get_app_tweet_text(self.request, vision)


class UserCreationForm (BaseUserCreationForm):
    class Meta:
        model = User
        fields = ("username",)

    # NOTE: We must override clean_username because of this bug:
    #       https://code.djangoproject.com/ticket/19353
    # TODO: Get rid of this whenever that patch gets merged in.
    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            self._meta.model._default_manager.get(username=username)
        except self._meta.model.DoesNotExist:
            return username
        from django import forms
        raise forms.ValidationError(self.error_messages['duplicate_username'])


class UserChangeForm (BaseUserChangeForm):
    class Meta:
        model = User


class UserAdmin (BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = BaseUserAdmin.list_display + ('date_joined', 'last_login', 'visible_on_home',)
    list_editable = BaseUserAdmin.list_editable + ('visible_on_home',)


admin.site.register(Moment)
admin.site.register(Vision, VisionAdmin)
admin.site.register(User, UserAdmin)
