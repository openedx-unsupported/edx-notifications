# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SQLNotificationMessage'
        db.create_table('notifications_notificationmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('payload', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('notifications', ['SQLNotificationMessage'])

        # Adding model 'SQLNotificationUserMap'
        db.create_table('notifications_notificationusermap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('msg', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['notifications.SQLNotificationMessage'])),
            ('read_at', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('user_context', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('notifications', ['SQLNotificationUserMap'])

        # Adding model 'SQLNotificationType'
        db.create_table('notifications_notificationtype', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256, primary_key=True)),
        ))
        db.send_create_signal('notifications', ['SQLNotificationType'])

        # Adding model 'SQLNotificationChannel'
        db.create_table('notifications_notificationchannel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('notifications', ['SQLNotificationChannel'])

        # Adding model 'SQLNotificationTypeRenderingProvided'
        db.create_table('notifications_notificationtyperenderingprovided', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('notifications', ['SQLNotificationTypeRenderingProvided'])

        # Adding model 'SQLNotificationUserTypeChannelMap'
        db.create_table('notifications_notificationusertypechannelmap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('notifications', ['SQLNotificationUserTypeChannelMap'])

        # Adding model 'SQLDisplayString'
        db.create_table('notifications_displaystring', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('string_name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('lang', self.gf('django.db.models.fields.CharField')(max_length=16, db_index=True)),
            ('string_value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('notifications', ['SQLDisplayString'])

        # Adding unique constraint on 'SQLDisplayString', fields ['string_name', 'lang']
        db.create_unique('notifications_displaystring', ['string_name', 'lang'])


    def backwards(self, orm):
        # Removing unique constraint on 'SQLDisplayString', fields ['string_name', 'lang']
        db.delete_unique('notifications_displaystring', ['string_name', 'lang'])

        # Deleting model 'SQLNotificationMessage'
        db.delete_table('notifications_notificationmessage')

        # Deleting model 'SQLNotificationUserMap'
        db.delete_table('notifications_notificationusermap')

        # Deleting model 'SQLNotificationType'
        db.delete_table('notifications_notificationtype')

        # Deleting model 'SQLNotificationChannel'
        db.delete_table('notifications_notificationchannel')

        # Deleting model 'SQLNotificationTypeRenderingProvided'
        db.delete_table('notifications_notificationtyperenderingprovided')

        # Deleting model 'SQLNotificationUserTypeChannelMap'
        db.delete_table('notifications_notificationusertypechannelmap')

        # Deleting model 'SQLDisplayString'
        db.delete_table('notifications_displaystring')


    models = {
        'notifications.sqldisplaystring': {
            'Meta': {'unique_together': "(('string_name', 'lang'),)", 'object_name': 'SQLDisplayString', 'db_table': "'notifications_displaystring'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '16', 'db_index': 'True'}),
            'string_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'string_value': ('django.db.models.fields.TextField', [], {})
        },
        'notifications.sqlnotificationchannel': {
            'Meta': {'object_name': 'SQLNotificationChannel', 'db_table': "'notifications_notificationchannel'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'notifications.sqlnotificationmessage': {
            'Meta': {'object_name': 'SQLNotificationMessage', 'db_table': "'notifications_notificationmessage'"},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'payload': ('django.db.models.fields.TextField', [], {})
        },
        'notifications.sqlnotificationtype': {
            'Meta': {'object_name': 'SQLNotificationType', 'db_table': "'notifications_notificationtype'"},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'primary_key': 'True'})
        },
        'notifications.sqlnotificationtyperenderingprovided': {
            'Meta': {'object_name': 'SQLNotificationTypeRenderingProvided', 'db_table': "'notifications_notificationtyperenderingprovided'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'notifications.sqlnotificationusermap': {
            'Meta': {'object_name': 'SQLNotificationUserMap', 'db_table': "'notifications_notificationusermap'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'msg': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['notifications.SQLNotificationMessage']"}),
            'read_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'user_context': ('django.db.models.fields.TextField', [], {}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        'notifications.sqlnotificationusertypechannelmap': {
            'Meta': {'object_name': 'SQLNotificationUserTypeChannelMap', 'db_table': "'notifications_notificationusertypechannelmap'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['notifications']