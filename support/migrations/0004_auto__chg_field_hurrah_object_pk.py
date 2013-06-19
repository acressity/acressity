# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Hurrah.object_pk'
        db.alter_column(u'support_hurrah', 'object_pk', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Hurrah.object_pk'
        raise RuntimeError("Cannot reverse this migration. 'Hurrah.object_pk' and its values cannot be restored.")

    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'experiences.experience': {
            'Meta': {'object_name': 'Experience'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'authored_experiences'", 'to': u"orm['explorers.Explorer']"}),
            'brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'experience': ('django.db.models.fields.CharField', [], {'max_length': '210'}),
            'gallery': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['photologue.Gallery']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'})
        },
        u'explorers.explorer': {
            'Meta': {'object_name': 'Explorer'},
            'birthdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'experiences': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'explorers'", 'symmetrical': 'False', 'to': u"orm['experiences.Experience']"}),
            'featured_experience': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'featured_experience'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['experiences.Experience']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'gallery': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'story_gallery'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['photologue.Gallery']", 'blank': 'True', 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'trailname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        u'photologue.gallery': {
            'Meta': {'ordering': "['-date_added']", 'object_name': 'Gallery'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_gallery'", 'to': u"orm['contenttypes.ContentType']"}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'explorers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'galleries'", 'symmetrical': 'False', 'to': u"orm['explorers.Explorer']"}),
            'featured_photo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['photologue.Photo']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'object_pk': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'photos': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'galleries'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['photologue.Photo']"}),
            'tags': ('photologue.models.TagField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'title_slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'photologue.photo': {
            'Meta': {'ordering': "['-date_added']", 'object_name': 'Photo'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['explorers.Explorer']", 'null': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'crop_from': ('django.db.models.fields.CharField', [], {'default': "'center'", 'max_length': '10', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'effect': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'photo_related'", 'null': 'True', 'to': u"orm['photologue.PhotoEffect']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tags': ('photologue.models.TagField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'title_slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'}),
            'view_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'photologue.photoeffect': {
            'Meta': {'object_name': 'PhotoEffect'},
            'background_color': ('django.db.models.fields.CharField', [], {'default': "'#FFFFFF'", 'max_length': '7'}),
            'brightness': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'color': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'contrast': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'filters': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'reflection_size': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'reflection_strength': ('django.db.models.fields.FloatField', [], {'default': '0.6'}),
            'sharpness': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'transpose_method': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'})
        },
        u'support.cheer': {
            'Meta': {'object_name': 'Cheer'},
            'cheerer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cheers_from'", 'to': u"orm['explorers.Explorer']"}),
            'date_cheered': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'explorer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cheers_for'", 'to': u"orm['explorers.Explorer']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'support.hurrah': {
            'Meta': {'object_name': 'Hurrah'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_hurrah'", 'to': u"orm['contenttypes.ContentType']"}),
            'explorer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['explorers.Explorer']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.TextField', [], {'null': 'True'})
        }
    }

    complete_apps = ['support']