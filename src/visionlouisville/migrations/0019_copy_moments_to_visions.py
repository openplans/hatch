# -*- coding: utf-8 -*-
import datetime
from itertools import islice
from south.db import db
from south.v2 import DataMigration
from django.db import models
from uuid import uuid1


def get_or_create_tweeter(orm, user_info):
    User = orm.User
    UserSocialAuth = orm['social_auth.UserSocialAuth']

    user_id = user_info['id']
    username = user_info['screen_name']
    try:
        user_social_auth = UserSocialAuth.objects.get(uid=user_id, provider='twitter')
        user = user_social_auth.user
    except UserSocialAuth.DoesNotExist:
        suffix = ''
        while True:
            user, created = User.objects.get_or_create(username=username + suffix)
            if created:
                user_full_name = user_info['name'].split(' ', 1)
                user.first_name = user_full_name[0]
                if len(user_full_name) > 1:
                    user.last_name = user_full_name[1]
                user.save()

                user_social_auth = UserSocialAuth.objects.create(
                    user=user,
                    uid=user_id,
                    provider='twitter',
                    extra_data='{"access_token": "oauth_token_secret=123&oauth_token=abc", "id": %s}' % (user_id,),
                )

                break
            else:
                suffix = str(uuid1())
    return user


def chunk(iterable, n):
    """Collect data into fixed-length chunks"""
    it = iter(iterable)
    while True:
        item = list(islice(it, n))
        if item: yield item
        else: break


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        moments = orm.Moment.objects.all()
        if moments.count() > 0:
            from visionlouisville.services import default_twitter_service as service
            screen_names = [moment.username for moment in moments]
            user_info_map = {}

            t = service.get_api()
            for screen_name_group in chunk(screen_names, 100):
                users_info = t.users.lookup(screen_name=','.join(screen_name_group))
                user_info_map.update(dict([
                    (user_info['screen_name'], user_info)
                    for user_info in users_info
                ]))

        for moment in moments:
            user_info = user_info_map.get(moment.username)
            orm.Vision.objects.create(
                text=moment.text,
                media_url=moment.media_url,
                author=get_or_create_tweeter(orm, user_info),
                created_at=moment.created_at,
                updated_at=moment.updated_at,
                tweet_id=moment.tweet_id
            )

    def backwards(self, orm):
        "Write your backwards methods here."
        visions = orm.Vision.objects.exclude(media_url='').exclude(media_url=None)
        for vision in visions:
            orm.Moment.objects.create(
                text=vision.text,
                media_url=vision.media_url,
                username=vision.author.username,
                created_at=vision.created_at,
                updated_at=vision.updated_at,
                tweet_id=vision.tweet_id
            )

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'social_auth.association': {
            'Meta': {'unique_together': "(('server_url', 'handle'),)", 'object_name': 'Association'},
            'assoc_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'handle': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issued': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'lifetime': ('django.db.models.fields.IntegerField', [], {}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'server_url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'social_auth.nonce': {
            'Meta': {'unique_together': "(('server_url', 'timestamp', 'salt'),)", 'object_name': 'Nonce'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'salt': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'server_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        'social_auth.usersocialauth': {
            'Meta': {'unique_together': "(('provider', 'uid'),)", 'object_name': 'UserSocialAuth'},
            'extra_data': ('social_auth.fields.JSONField', [], {'default': "'{}'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provider': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'social_auth'", 'to': u"orm['visionlouisville.User']"})
        },
        u'visionlouisville.moment': {
            'Meta': {'ordering': "('-created_at',)", 'object_name': 'Moment'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tweet_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'visionlouisville.reply': {
            'Meta': {'ordering': "('created_at',)", 'object_name': 'Reply'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'replies'", 'to': u"orm['visionlouisville.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '140', 'blank': 'True'}),
            'tweet_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'vision': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'replies'", 'to': u"orm['visionlouisville.Vision']"})
        },
        u'visionlouisville.share': {
            'Meta': {'object_name': 'Share'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tweet_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shares'", 'to': u"orm['visionlouisville.User']"}),
            'vision': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['visionlouisville.Vision']"})
        },
        u'visionlouisville.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'visible_on_home': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'visionlouisville.vision': {
            'Meta': {'ordering': "('-created_at',)", 'object_name': 'Vision'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'visions'", 'to': u"orm['visionlouisville.User']"}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inspiration': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['visionlouisville.Moment']", 'null': 'True', 'blank': 'True'}),
            'media_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'sharers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'sharers'", 'blank': 'True', 'through': u"orm['visionlouisville.Share']", 'to': u"orm['visionlouisville.User']"}),
            'supporters': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'supported'", 'blank': 'True', 'to': u"orm['visionlouisville.User']"}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tweet_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['visionlouisville']
    symmetrical = True
