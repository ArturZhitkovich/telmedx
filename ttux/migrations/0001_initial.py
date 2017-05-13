# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Adding model 'mobileCam'
        db.create_table('ttux_mobilecam', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('groups', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('uid', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('streamId', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('connectedState', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ttux', ['mobileCam'])

        # Adding model 'sessionRecord'
        db.create_table('ttux_sessionrecord', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mobile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ttux.mobileCam'])),
            ('sessn_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('streamId', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('userId', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('ttux', ['sessionRecord'])

        # Adding model 'sessionLog'
        db.create_table('ttux_sessionlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ttux.mobileCam'])),
            ('begin_timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('frames', self.gf('django.db.models.fields.IntegerField')()),
            ('captured_images', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('ttux', ['sessionLog'])

    def backwards(self, orm):
        # Deleting model 'mobileCam'
        db.delete_table('ttux_mobilecam')

        # Deleting model 'sessionRecord'
        db.delete_table('ttux_sessionrecord')

        # Deleting model 'sessionLog'
        db.delete_table('ttux_sessionlog')

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
            'groups': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'streamId': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
