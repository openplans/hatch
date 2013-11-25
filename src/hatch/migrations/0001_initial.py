# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ("visionlouisville", "0039_auto__add_field_appconfig_visionaries_label__add_field_appconfig_allie"),
    )

    def forwards(self, orm):
        db.rename_table('visionlouisville_appconfig', 'hatch_appconfig')
        db.rename_table('visionlouisville_category', 'hatch_category')
        db.rename_table('visionlouisville_reply', 'hatch_reply')
        db.rename_table('visionlouisville_share', 'hatch_share')
        db.rename_table('visionlouisville_tweet', 'hatch_tweet')
        db.rename_table('visionlouisville_user', 'hatch_user')
        db.rename_table('visionlouisville_user_groups', 'hatch_user_groups')
        db.rename_table('visionlouisville_user_user_permissions', 'hatch_user_user_permissions')
        db.rename_table('visionlouisville_vision', 'hatch_vision')
        db.rename_table('visionlouisville_vision_supporters', 'hatch_vision_supporters')

    def backwards(self, orm):
        db.rename_table('hatch_appconfig', 'visionlouisville_appconfig')
        db.rename_table('hatch_category', 'visionlouisville_category')
        db.rename_table('hatch_reply', 'visionlouisville_reply')
        db.rename_table('hatch_share', 'visionlouisville_share')
        db.rename_table('hatch_tweet', 'visionlouisville_tweet')
        db.rename_table('hatch_user', 'visionlouisville_user')
        db.rename_table('hatch_user_groups', 'visionlouisville_user_groups')
        db.rename_table('hatch_user_user_permissions', 'visionlouisville_user_user_permissions')
        db.rename_table('hatch_vision', 'visionlouisville_vision')
        db.rename_table('hatch_vision_supporters', 'visionlouisville_vision_supporters')

    # def forwards(self, orm):
    #     # Adding model 'User'
    #     db.create_table(u'hatch_user', (
    #         (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
    #         ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
    #         ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
    #         ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
    #         ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
    #         ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
    #         ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
    #         ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
    #         ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
    #         ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
    #         ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
    #         ('visible_on_home', self.gf('django.db.models.fields.BooleanField')(default=True)),
    #         ('checked_notifications_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
    #         ('sm_not_found', self.gf('django.db.models.fields.BooleanField')(default=False)),
    #     ))
    #     db.send_create_signal(u'hatch', ['User'])

    #     # Adding M2M table for field groups on 'User'
    #     m2m_table_name = db.shorten_name(u'hatch_user_groups')
    #     db.create_table(m2m_table_name, (
    #         ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
    #         ('user', models.ForeignKey(orm[u'hatch.user'], null=False)),
    #         ('group', models.ForeignKey(orm[u'auth.group'], null=False))
    #     ))
    #     db.create_unique(m2m_table_name, ['user_id', 'group_id'])

    #     # Adding M2M table for field user_permissions on 'User'
    #     m2m_table_name = db.shorten_name(u'hatch_user_user_permissions')
    #     db.create_table(m2m_table_name, (
    #         ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
    #         ('user', models.ForeignKey(orm[u'hatch.user'], null=False)),
    #         ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
    #     ))
    #     db.create_unique(m2m_table_name, ['user_id', 'permission_id'])

    #     # Adding model 'Tweet'
    #     db.create_table(u'hatch_tweet', (
    #         ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
    #         ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
    #         ('tweet_id', self.gf('django.db.models.fields.CharField')(max_length=64, primary_key=True)),
    #         ('tweet_data', self.gf('jsonfield.fields.JSONField')(default={}, blank=True)),
    #         ('tweet_user_id', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
    #         ('tweet_user_screen_name', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
    #         ('in_reply_to', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tweet_replies', null=True, to=orm['hatch.Tweet'])),
    #     ))
    #     db.send_create_signal(u'hatch', ['Tweet'])

    #     # Adding model 'Category'
    #     db.create_table(u'hatch_category', (
    #         ('name', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
    #         ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
    #         ('prompt', self.gf('django.db.models.fields.TextField')()),
    #         ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
    #         ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
    #     ))
    #     db.send_create_signal(u'hatch', ['Category'])

    #     # Adding model 'Vision'
    #     db.create_table(u'hatch_vision', (
    #         (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
    #         ('app_tweet', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='app_tweeted_vision', unique=True, null=True, to=orm['hatch.Tweet'])),
    #         ('tweet', self.gf('django.db.models.fields.related.OneToOneField')(related_name='user_tweeted_vision', unique=True, null=True, to=orm['hatch.Tweet'])),
    #         ('tweeted_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
    #         ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='visions', to=orm['hatch.User'])),
    #         ('category', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='visions', null=True, to=orm['hatch.Category'])),
    #         ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
    #         ('media_url', self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True)),
    #         ('featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
    #         ('created_at', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
    #         ('updated_at', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
    #     ))
    #     db.send_create_signal(u'hatch', ['Vision'])

    #     # Adding M2M table for field supporters on 'Vision'
    #     m2m_table_name = db.shorten_name(u'hatch_vision_supporters')
    #     db.create_table(m2m_table_name, (
    #         ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
    #         ('vision', models.ForeignKey(orm[u'hatch.vision'], null=False)),
    #         ('user', models.ForeignKey(orm[u'hatch.user'], null=False))
    #     ))
    #     db.create_unique(m2m_table_name, ['vision_id', 'user_id'])

    #     # Adding model 'Share'
    #     db.create_table(u'hatch_share', (
    #         (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
    #         ('vision', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hatch.Vision'])),
    #         ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='shares', to=orm['hatch.User'])),
    #         ('tweet', self.gf('django.db.models.fields.related.ForeignKey')(related_name='shares', to=orm['hatch.Tweet'])),
    #     ))
    #     db.send_create_signal(u'hatch', ['Share'])

    #     # Adding model 'Reply'
    #     db.create_table(u'hatch_reply', (
    #         (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
    #         ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
    #         ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
    #         ('tweet', self.gf('django.db.models.fields.related.OneToOneField')(related_name='reply', unique=True, to=orm['hatch.Tweet'])),
    #         ('tweeted_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
    #         ('vision', self.gf('django.db.models.fields.related.ForeignKey')(related_name='replies', to=orm['hatch.Vision'])),
    #         ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='replies', to=orm['hatch.User'])),
    #         ('text', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
    #     ))
    #     db.send_create_signal(u'hatch', ['Reply'])

    #     # Adding model 'AppConfig'
    #     db.create_table(u'hatch_appconfig', (
    #         (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
    #         ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
    #         ('subtitle', self.gf('django.db.models.fields.CharField')(max_length=100)),
    #         ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
    #         ('description', self.gf('django.db.models.fields.TextField')()),
    #         ('twitter_handle', self.gf('django.db.models.fields.CharField')(max_length=50)),
    #         ('share_title', self.gf('django.db.models.fields.CharField')(max_length=100)),
    #         ('url', self.gf('django.db.models.fields.CharField')(max_length=1024)),
    #         ('vision', self.gf('django.db.models.fields.CharField')(max_length=50)),
    #         ('vision_plural', self.gf('django.db.models.fields.CharField')(max_length=50)),
    #         ('visionary', self.gf('django.db.models.fields.CharField')(max_length=50)),
    #         ('visionary_plural', self.gf('django.db.models.fields.CharField')(max_length=50)),
    #         ('visionaries_label', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
    #         ('ally', self.gf('django.db.models.fields.CharField')(max_length=50)),
    #         ('ally_plural', self.gf('django.db.models.fields.CharField')(max_length=50)),
    #         ('allies_label', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
    #         ('city', self.gf('django.db.models.fields.CharField')(max_length=50)),
    #         ('welcome_prompt', self.gf('django.db.models.fields.CharField')(max_length=1024)),
    #     ))
    #     db.send_create_signal(u'hatch', ['AppConfig'])


    # def backwards(self, orm):
    #     # Deleting model 'User'
    #     db.delete_table(u'hatch_user')

    #     # Removing M2M table for field groups on 'User'
    #     db.delete_table(db.shorten_name(u'hatch_user_groups'))

    #     # Removing M2M table for field user_permissions on 'User'
    #     db.delete_table(db.shorten_name(u'hatch_user_user_permissions'))

    #     # Deleting model 'Tweet'
    #     db.delete_table(u'hatch_tweet')

    #     # Deleting model 'Category'
    #     db.delete_table(u'hatch_category')

    #     # Deleting model 'Vision'
    #     db.delete_table(u'hatch_vision')

    #     # Removing M2M table for field supporters on 'Vision'
    #     db.delete_table(db.shorten_name(u'hatch_vision_supporters'))

    #     # Deleting model 'Share'
    #     db.delete_table(u'hatch_share')

    #     # Deleting model 'Reply'
    #     db.delete_table(u'hatch_reply')

    #     # Deleting model 'AppConfig'
    #     db.delete_table(u'hatch_appconfig')


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
        u'hatch.appconfig': {
            'Meta': {'object_name': 'AppConfig'},
            'allies_label': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
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
            'visionaries_label': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'visionary': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'visionary_plural': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'welcome_prompt': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        u'hatch.category': {
            'Meta': {'object_name': 'Category'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'prompt': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'hatch.reply': {
            'Meta': {'ordering': "('tweeted_at',)", 'object_name': 'Reply'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'replies'", 'to': u"orm['hatch.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'tweet': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'reply'", 'unique': 'True', 'to': u"orm['hatch.Tweet']"}),
            'tweeted_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'vision': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'replies'", 'to': u"orm['hatch.Vision']"})
        },
        u'hatch.share': {
            'Meta': {'object_name': 'Share'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tweet': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shares'", 'to': u"orm['hatch.Tweet']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shares'", 'to': u"orm['hatch.User']"}),
            'vision': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hatch.Vision']"})
        },
        u'hatch.tweet': {
            'Meta': {'object_name': 'Tweet'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'in_reply_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tweet_replies'", 'null': 'True', 'to': u"orm['hatch.Tweet']"}),
            'tweet_data': ('jsonfield.fields.JSONField', [], {'default': '{}', 'blank': 'True'}),
            'tweet_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'}),
            'tweet_user_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'tweet_user_screen_name': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'hatch.user': {
            'Meta': {'object_name': 'User'},
            'checked_notifications_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
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
            'sm_not_found': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'visible_on_home': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'hatch.vision': {
            'Meta': {'ordering': "('-tweeted_at',)", 'object_name': 'Vision'},
            'app_tweet': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'app_tweeted_vision'", 'unique': 'True', 'null': 'True', 'to': u"orm['hatch.Tweet']"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'visions'", 'to': u"orm['hatch.User']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'visions'", 'null': 'True', 'to': u"orm['hatch.Category']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'sharers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'sharers'", 'blank': 'True', 'through': u"orm['hatch.Share']", 'to': u"orm['hatch.User']"}),
            'supporters': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'supported'", 'blank': 'True', 'to': u"orm['hatch.User']"}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tweet': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'user_tweeted_vision'", 'unique': 'True', 'null': 'True', 'to': u"orm['hatch.Tweet']"}),
            'tweeted_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['hatch']