# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SQLNotificationType'
        db.create_table('edx_notifications_notificationtype', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
        ))
        db.send_create_signal('edx_notifications', ['SQLNotificationType'])

        # Adding model 'SQLNotificationMessage'
        db.create_table('edx_notifications_notificationmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('namespace', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_index=True)),
            ('msg_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['edx_notifications.SQLNotificationType'])),
            ('from_user_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('payload', self.gf('django.db.models.fields.TextField')()),
            ('deliver_no_earlier_than', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('expires_at', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('expires_secs_after_read', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('edx_notifications', ['SQLNotificationMessage'])

        # Adding model 'SQLUserNotification'
        db.create_table('edx_notifications_usernotification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('msg', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['edx_notifications.SQLNotificationMessage'])),
            ('read_at', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('user_context', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('edx_notifications', ['SQLUserNotification'])

        # Adding unique constraint on 'SQLUserNotification', fields ['user_id', 'msg']
        db.create_unique('edx_notifications_usernotification', ['user_id', 'msg_id'])

        # Adding model 'SQLNotificationChannel'
        db.create_table('edx_notifications_notificationchannel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('edx_notifications', ['SQLNotificationChannel'])

        # Adding model 'SQLUserNotificationPreferences'
        db.create_table('edx_notifications_usernotificationpreferences', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('edx_notifications', ['SQLUserNotificationPreferences'])


    def backwards(self, orm):
        # Removing unique constraint on 'SQLUserNotification', fields ['user_id', 'msg']
        db.delete_unique('edx_notifications_usernotification', ['user_id', 'msg_id'])

        # Deleting model 'SQLNotificationType'
        db.delete_table('edx_notifications_notificationtype')

        # Deleting model 'SQLNotificationMessage'
        db.delete_table('edx_notifications_notificationmessage')

        # Deleting model 'SQLUserNotification'
        db.delete_table('edx_notifications_usernotification')

        # Deleting model 'SQLNotificationChannel'
        db.delete_table('edx_notifications_notificationchannel')

        # Deleting model 'SQLUserNotificationPreferences'
        db.delete_table('edx_notifications_usernotificationpreferences')


    models = {
        'edx_notifications.sqlnotificationchannel': {
            'Meta': {'object_name': 'SQLNotificationChannel', 'db_table': "'edx_notifications_notificationchannel'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'edx_notifications.sqlnotificationmessage': {
            'Meta': {'ordering': "['-created']", 'object_name': 'SQLNotificationMessage', 'db_table': "'edx_notifications_notificationmessage'"},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'deliver_no_earlier_than': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'expires_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'expires_secs_after_read': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'from_user_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'msg_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['edx_notifications.SQLNotificationType']"}),
            'namespace': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_index': 'True'}),
            'payload': ('django.db.models.fields.TextField', [], {}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'edx_notifications.sqlnotificationtype': {
            'Meta': {'object_name': 'SQLNotificationType', 'db_table': "'edx_notifications_notificationtype'"},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        'edx_notifications.sqlusernotification': {
            'Meta': {'ordering': "['-created']", 'unique_together': "(('user_id', 'msg'),)", 'object_name': 'SQLUserNotification', 'db_table': "'edx_notifications_usernotification'"},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'msg': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['edx_notifications.SQLNotificationMessage']"}),
            'read_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'user_context': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        'edx_notifications.sqlusernotificationpreferences': {
            'Meta': {'object_name': 'SQLUserNotificationPreferences', 'db_table': "'edx_notifications_usernotificationpreferences'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['edx_notifications']