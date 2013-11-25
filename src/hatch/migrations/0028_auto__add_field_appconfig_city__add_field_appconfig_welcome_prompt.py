# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'AppConfig.city'
        db.add_column(u'visionlouisville_appconfig', 'city',
                      self.gf('django.db.models.fields.CharField')(default='our city', max_length=50),
                      keep_default=False)

        # Adding field 'AppConfig.welcome_prompt'
        db.add_column(u'visionlouisville_appconfig', 'welcome_prompt',
                      self.gf('django.db.models.fields.CharField')(default='Welcome!', max_length=1024),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'AppConfig.city'
        db.delete_column(u'visionlouisville_appconfig', 'city')

        # Deleting field 'AppConfig.welcome_prompt'
        db.delete_column(u'visionlouisville_appconfig', 'welcome_prompt')


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
        u'visionlouisville.appconfig': {
            'Meta': {'object_name': 'AppConfig'},
            'ally': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ally_plural': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'share_title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'twitter_handle': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'vision': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'vision_plural': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'visionary': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'visionary_plural': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'welcome_prompt': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        u'visionlouisville.category': {
            'Meta': {'object_name': 'Category'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'prompt': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'visionlouisville.reply': {
            'Meta': {'ordering': "('created_at',)", 'object_name': 'Reply'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'replies'", 'to': u"orm['visionlouisville.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '140', 'blank': 'True'}),
            'tweet': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'reply'", 'unique': 'True', 'to': u"orm['visionlouisville.Tweet']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'vision': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'replies'", 'to': u"orm['visionlouisville.Vision']"})
        },
        u'visionlouisville.share': {
            'Meta': {'object_name': 'Share'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tweet': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shares'", 'to': u"orm['visionlouisville.Tweet']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shares'", 'to': u"orm['visionlouisville.User']"}),
            'vision': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['visionlouisville.Vision']"})
        },
        u'visionlouisville.tweet': {
            'Meta': {'object_name': 'Tweet'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'in_reply_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tweet_replies'", 'null': 'True', 'to': u"orm['visionlouisville.Tweet']"}),
            'tweet_data': ('jsonfield.fields.JSONField', [], {'default': '{}', 'blank': 'True'}),
            'tweet_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'visions'", 'null': 'True', 'to': u"orm['visionlouisville.Category']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'sharers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'sharers'", 'blank': 'True', 'through': u"orm['visionlouisville.Share']", 'to': u"orm['visionlouisville.User']"}),
            'supporters': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'supported'", 'blank': 'True', 'to': u"orm['visionlouisville.User']"}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tweet': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'vision'", 'unique': 'True', 'null': 'True', 'to': u"orm['visionlouisville.Tweet']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['visionlouisville']