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

        # Adding model 'SQLNotificationUserMap'
        db.create_table('edx_notifications_notificationusermap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('msg', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['edx_notifications.SQLNotificationMessage'])),
            ('read_at', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('user_context', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('edx_notifications', ['SQLNotificationUserMap'])

        # Adding unique constraint on 'SQLNotificationUserMap', fields ['user_id', 'msg']
        db.create_unique('edx_notifications_notificationusermap', ['user_id', 'msg_id'])

        # Adding model 'SQLNotificationChannel'
        db.create_table('edx_notifications_notificationchannel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('edx_notifications', ['SQLNotificationChannel'])

        # Adding model 'SQLNotificationTypeRenderingProvided'
        db.create_table('edx_notifications_notificationtyperenderingprovided', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('edx_notifications', ['SQLNotificationTypeRenderingProvided'])

        # Adding model 'SQLNotificationUserTypeChannelMap'
        db.create_table('edx_notifications_notificationusertypechannelmap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('edx_notifications', ['SQLNotificationUserTypeChannelMap'])

        # Adding model 'SQLDisplayString'
        db.create_table('edx_notifications_displaystring', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('string_name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('lang', self.gf('django.db.models.fields.CharField')(max_length=16, db_index=True)),
            ('string_value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('edx_notifications', ['SQLDisplayString'])

        # Adding unique constraint on 'SQLDisplayString', fields ['string_name', 'lang']
        db.create_unique('edx_notifications_displaystring', ['string_name', 'lang'])


    def backwards(self, orm):
        # Removing unique constraint on 'SQLDisplayString', fields ['string_name', 'lang']
        db.delete_unique('edx_notifications_displaystring', ['string_name', 'lang'])

        # Removing unique constraint on 'SQLNotificationUserMap', fields ['user_id', 'msg']
        db.delete_unique('edx_notifications_notificationusermap', ['user_id', 'msg_id'])

        # Deleting model 'SQLNotificationType'
        db.delete_table('edx_notifications_notificationtype')

        # Deleting model 'SQLNotificationMessage'
        db.delete_table('edx_notifications_notificationmessage')

        # Deleting model 'SQLNotificationUserMap'
        db.delete_table('edx_notifications_notificationusermap')

        # Deleting model 'SQLNotificationChannel'
        db.delete_table('edx_notifications_notificationchannel')

        # Deleting model 'SQLNotificationTypeRenderingProvided'
        db.delete_table('edx_notifications_notificationtyperenderingprovided')

        # Deleting model 'SQLNotificationUserTypeChannelMap'
        db.delete_table('edx_notifications_notificationusertypechannelmap')

        # Deleting model 'SQLDisplayString'
        db.delete_table('edx_notifications_displaystring')


    models = {
        'edx_notifications.sqldisplaystring': {
            'Meta': {'unique_together': "(('string_name', 'lang'),)", 'object_name': 'SQLDisplayString', 'db_table': "'edx_notifications_displaystring'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '16', 'db_index': 'True'}),
            'string_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'string_value': ('django.db.models.fields.TextField', [], {})
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
            'payload': ('django.db.models.fields.TextField', [], {}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'edx_notifications.sqlnotificationtype': {
            'Meta': {'object_name': 'SQLNotificationType', 'db_table': "'edx_notifications_notificationtype'"},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        'edx_notifications.sqlnotificationtyperenderingprovided': {
            'Meta': {'object_name': 'SQLNotificationTypeRenderingProvided', 'db_table': "'edx_notifications_notificationtyperenderingprovided'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'edx_notifications.sqlnotificationusermap': {
            'Meta': {'ordering': "['-created']", 'unique_together': "(('user_id', 'msg'),)", 'object_name': 'SQLNotificationUserMap', 'db_table': "'edx_notifications_notificationusermap'"},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'msg': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['edx_notifications.SQLNotificationMessage']"}),
            'read_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'user_context': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        'edx_notifications.sqlnotificationusertypechannelmap': {
            'Meta': {'object_name': 'SQLNotificationUserTypeChannelMap', 'db_table': "'edx_notifications_notificationusertypechannelmap'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['edx_notifications']