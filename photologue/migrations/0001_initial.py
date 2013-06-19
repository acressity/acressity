# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Gallery'
        db.create_table(u'photologue_gallery', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('title_slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tags', self.gf('photologue.models.TagField')(max_length=255, blank=True)),
            ('featured_photo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['photologue.Photo'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='content_type_set_for_gallery', to=orm['contenttypes.ContentType'])),
            ('object_pk', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal(u'photologue', ['Gallery'])

        # Adding M2M table for field photos on 'Gallery'
        db.create_table(u'photologue_gallery_photos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gallery', models.ForeignKey(orm[u'photologue.gallery'], null=False)),
            ('photo', models.ForeignKey(orm[u'photologue.photo'], null=False))
        ))
        db.create_unique(u'photologue_gallery_photos', ['gallery_id', 'photo_id'])

        # Adding M2M table for field explorers on 'Gallery'
        db.create_table(u'photologue_gallery_explorers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gallery', models.ForeignKey(orm[u'photologue.gallery'], null=False)),
            ('explorer', models.ForeignKey(orm[u'explorers.explorer'], null=False))
        ))
        db.create_unique(u'photologue_gallery_explorers', ['gallery_id', 'explorer_id'])

        # Adding model 'GalleryUpload'
        db.create_table(u'photologue_galleryupload', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zip_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('gallery', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['photologue.Gallery'], null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tags', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'photologue', ['GalleryUpload'])

        # Adding model 'Photo'
        db.create_table(u'photologue_photo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('date_taken', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('view_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('crop_from', self.gf('django.db.models.fields.CharField')(default='center', max_length=10, blank=True)),
            ('effect', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='photo_related', null=True, to=orm['photologue.PhotoEffect'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('title_slug', self.gf('django.db.models.fields.SlugField')(max_length=50, blank=True)),
            ('caption', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tags', self.gf('photologue.models.TagField')(max_length=255, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['explorers.Explorer'], null=True)),
        ))
        db.send_create_signal(u'photologue', ['Photo'])

        # Adding model 'PhotoEffect'
        db.create_table(u'photologue_photoeffect', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('transpose_method', self.gf('django.db.models.fields.CharField')(max_length=15, blank=True)),
            ('color', self.gf('django.db.models.fields.FloatField')(default=1.0)),
            ('brightness', self.gf('django.db.models.fields.FloatField')(default=1.0)),
            ('contrast', self.gf('django.db.models.fields.FloatField')(default=1.0)),
            ('sharpness', self.gf('django.db.models.fields.FloatField')(default=1.0)),
            ('filters', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('reflection_size', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('reflection_strength', self.gf('django.db.models.fields.FloatField')(default=0.6)),
            ('background_color', self.gf('django.db.models.fields.CharField')(default='#FFFFFF', max_length=7)),
        ))
        db.send_create_signal(u'photologue', ['PhotoEffect'])

        # Adding model 'Watermark'
        db.create_table(u'photologue_watermark', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('style', self.gf('django.db.models.fields.CharField')(default='scale', max_length=5)),
            ('opacity', self.gf('django.db.models.fields.FloatField')(default=1)),
        ))
        db.send_create_signal(u'photologue', ['Watermark'])

        # Adding model 'PhotoSize'
        db.create_table(u'photologue_photosize', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('height', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('quality', self.gf('django.db.models.fields.PositiveIntegerField')(default=70)),
            ('upscale', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('crop', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pre_cache', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('increment_count', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('effect', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='photo_sizes', null=True, to=orm['photologue.PhotoEffect'])),
            ('watermark', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='photo_sizes', null=True, to=orm['photologue.Watermark'])),
        ))
        db.send_create_signal(u'photologue', ['PhotoSize'])


    def backwards(self, orm):
        # Deleting model 'Gallery'
        db.delete_table(u'photologue_gallery')

        # Removing M2M table for field photos on 'Gallery'
        db.delete_table('photologue_gallery_photos')

        # Removing M2M table for field explorers on 'Gallery'
        db.delete_table('photologue_gallery_explorers')

        # Deleting model 'GalleryUpload'
        db.delete_table(u'photologue_galleryupload')

        # Deleting model 'Photo'
        db.delete_table(u'photologue_photo')

        # Deleting model 'PhotoEffect'
        db.delete_table(u'photologue_photoeffect')

        # Deleting model 'Watermark'
        db.delete_table(u'photologue_watermark')

        # Deleting model 'PhotoSize'
        db.delete_table(u'photologue_photosize')


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
            'experience': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
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
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
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
        u'photologue.galleryupload': {
            'Meta': {'object_name': 'GalleryUpload'},
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'gallery': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['photologue.Gallery']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'zip_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
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
        u'photologue.photosize': {
            'Meta': {'ordering': "['width', 'height']", 'object_name': 'PhotoSize'},
            'crop': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'effect': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'photo_sizes'", 'null': 'True', 'to': u"orm['photologue.PhotoEffect']"}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'increment_count': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'pre_cache': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'quality': ('django.db.models.fields.PositiveIntegerField', [], {'default': '70'}),
            'upscale': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'watermark': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'photo_sizes'", 'null': 'True', 'to': u"orm['photologue.Watermark']"}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'photologue.watermark': {
            'Meta': {'object_name': 'Watermark'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'opacity': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'style': ('django.db.models.fields.CharField', [], {'default': "'scale'", 'max_length': '5'})
        }
    }

    complete_apps = ['photologue']