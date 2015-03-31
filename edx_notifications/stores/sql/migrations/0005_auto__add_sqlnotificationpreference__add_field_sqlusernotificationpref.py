# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SQLNotificationPreference'
        db.create_table('edx_notifications_notificationpreference', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('display_description', self.gf('django.db.models.fields.CharField')(max_length=1023)),
        ))
        db.send_create_signal('edx_notifications', ['SQLNotificationPreference'])

        # Adding field 'SQLUserNotificationPreferences.created'
        db.add_column('edx_notifications_usernotificationpreferences', 'created',
                      self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'SQLUserNotificationPreferences.modified'
        db.add_column('edx_notifications_usernotificationpreferences', 'modified',
                      self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'SQLUserNotificationPreferences.user_id'
        db.add_column('edx_notifications_usernotificationpreferences', 'user_id',
                      self.gf('django.db.models.fields.IntegerField')(default=-1, db_index=True),
                      keep_default=False)

        # Adding field 'SQLUserNotificationPreferences.preference'
        db.add_column('edx_notifications_usernotificationpreferences', 'preference',
                      self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['edx_notifications.SQLNotificationPreference']),
                      keep_default=False)

        # Adding field 'SQLUserNotificationPreferences.value'
        db.add_column('edx_notifications_usernotificationpreferences', 'value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)


        # Changing field 'SQLNotificationMessage.object_id'
        db.alter_column('edx_notifications_notificationmessage', 'object_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    def backwards(self, orm):
        # Deleting model 'SQLNotificationPreference'
        db.delete_table('edx_notifications_notificationpreference')

        # Deleting field 'SQLUserNotificationPreferences.created'
        db.delete_column('edx_notifications_usernotificationpreferences', 'created')

        # Deleting field 'SQLUserNotificationPreferences.modified'
        db.delete_column('edx_notifications_usernotificationpreferences', 'modified')

        # Deleting field 'SQLUserNotificationPreferences.user_id'
        db.delete_column('edx_notifications_usernotificationpreferences', 'user_id')

        # Deleting field 'SQLUserNotificationPreferences.preference'
        db.delete_column('edx_notifications_usernotificationpreferences', 'preference_id')

        # Deleting field 'SQLUserNotificationPreferences.value'
        db.delete_column('edx_notifications_usernotificationpreferences', 'value')


        # Changing field 'SQLNotificationMessage.object_id'
        db.alter_column('edx_notifications_notificationmessage', 'object_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))

    models = {
        'edx_notifications.sqlnotificationcallbacktimer': {
            'Meta': {'object_name': 'SQLNotificationCallbackTimer', 'db_table': "'edx_notifications_notificationcallbacktimer'"},
            'callback_at': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'context': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'err_msg': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'executed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'periodicity_min': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'results': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
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
            'object_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'db_index': 'True'}),
            'payload': ('django.db.models.fields.TextField', [], {}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resolve_links': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        'edx_notifications.sqlnotificationpreference': {
            'Meta': {'object_name': 'SQLNotificationPreference', 'db_table': "'edx_notifications_notificationpreference'"},
            'display_description': ('django.db.models.fields.CharField', [], {'max_length': '1023'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        'edx_notifications.sqlnotificationtype': {
            'Meta': {'object_name': 'SQLNotificationType', 'db_table': "'edx_notifications_notificationtype'"},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'renderer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'renderer_context': ('django.db.models.fields.TextField', [], {'null': 'True'})
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
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'preference': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['edx_notifications.SQLNotificationPreference']"}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['edx_notifications']