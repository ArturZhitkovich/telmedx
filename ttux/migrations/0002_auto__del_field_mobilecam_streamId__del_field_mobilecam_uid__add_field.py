# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Deleting field 'mobileCam.streamId'
        db.delete_column('ttux_mobilecam', 'streamId')

        # Deleting field 'mobileCam.uid'
        db.delete_column('ttux_mobilecam', 'uid')

        # Adding field 'mobileCam.email'
        db.add_column('ttux_mobilecam', 'email',
                      self.gf('django.db.models.fields.EmailField')(default='', max_length=254),
                      keep_default=False)

        # Adding field 'mobileCam.last_name'
        db.add_column('ttux_mobilecam', 'last_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=70),
                      keep_default=False)

        # Adding field 'mobileCam.first_name'
        db.add_column('ttux_mobilecam', 'first_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=35),
                      keep_default=False)

        # Adding field 'mobileCam.phone_number'
        db.add_column('ttux_mobilecam', 'phone_number',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10),
                      keep_default=False)

    def backwards(self, orm):
        # Adding field 'mobileCam.streamId'
        db.add_column('ttux_mobilecam', 'streamId',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'mobileCam.uid'
        db.add_column('ttux_mobilecam', 'uid',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50),
                      keep_default=False)

        # Deleting field 'mobileCam.email'
        db.delete_column('ttux_mobilecam', 'email')

        # Deleting field 'mobileCam.last_name'
        db.delete_column('ttux_mobilecam', 'last_name')

        # Deleting field 'mobileCam.first_name'
        db.delete_column('ttux_mobilecam', 'first_name')

        # Deleting field 'mobileCam.phone_number'
        db.delete_column('ttux_mobilecam', 'phone_number')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [],
                            {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')",
                     'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': (
            'django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)",
                     'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ttux.mobilecam': {
            'Meta': {'object_name': 'mobileCam'},
            'connectedState': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '254'}),
            'first_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '35'}),
            'groups': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '70'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'})
        },
        'ttux.sessionlog': {
            'Meta': {'object_name': 'sessionLog'},
            'begin_timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'captured_images': ('django.db.models.fields.IntegerField', [], {}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ttux.mobileCam']"}),
            'end_timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'frames': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'ttux.sessionrecord': {
            'Meta': {'object_name': 'sessionRecord'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ttux.mobileCam']"}),
            'sessn_date': ('django.db.models.fields.DateTimeField', [], {}),
            'streamId': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'userId': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['ttux']
