# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import photologue.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_added', models.DateTimeField(default=datetime.datetime.now, verbose_name='date published')),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('title_slug', models.SlugField(help_text='A "slug" is a unique URL-                                    friendly title for an object.', verbose_name='title slug')),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('is_public', models.BooleanField(default=True, verbose_name='is public')),
                ('tags', photologue.models.TagField(help_text='Django-tagging was not found,         tags will be treated as plain text.', max_length=255, verbose_name='tags', blank=True)),
                ('object_pk', models.TextField(null=True, verbose_name='object ID')),
                ('content_type', models.ForeignKey(related_name='content_type_set_for_gallery', verbose_name='content type', to='contenttypes.ContentType')),
                ('explorers', models.ManyToManyField(related_name='galleries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date_added'],
                'get_latest_by': 'date_added',
                'verbose_name': 'gallery',
                'verbose_name_plural': 'galleries',
            },
        ),
        migrations.CreateModel(
            name='GalleryUpload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('zip_file', models.FileField(help_text='Select a .zip file of images to upload into a new Gallery.', upload_to=b'/temp', verbose_name='images file (.zip)')),
                ('title', models.CharField(help_text='All photos in the gallery will be given a title made up of the gallery title + a sequential number.', max_length=50, verbose_name='title')),
                ('caption', models.TextField(help_text='Caption will be added to all photos.', verbose_name='caption', blank=True)),
                ('description', models.TextField(help_text='A description of this Gallery.', verbose_name='description', blank=True)),
                ('is_public', models.BooleanField(default=True, help_text='Uncheck this to make the uploaded gallery and included photographs private.', verbose_name='is public')),
                ('tags', models.CharField(help_text='Django-tagging was not found,         tags will be treated as plain text.', max_length=255, verbose_name='tags', blank=True)),
                ('gallery', models.ForeignKey(blank=True, to='photologue.Gallery', help_text='Select a gallery to add these images to. leave this empty to create a new gallery from the supplied title.', null=True)),
            ],
            options={
                'verbose_name': 'gallery upload',
                'verbose_name_plural': 'gallery uploads',
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=photologue.models.get_storage_path, verbose_name='image')),
                ('date_taken', models.DateTimeField(verbose_name='date taken', null=True, editable=False, blank=True)),
                ('view_count', models.PositiveIntegerField(default=0, editable=False)),
                ('crop_from', models.CharField(default=b'center', max_length=10, verbose_name='crop from', blank=True, choices=[(b'top', 'Top'), (b'right', 'Right'), (b'bottom', 'Bottom'), (b'left', 'Left'), (b'center', 'Center (Default)')])),
                ('title', models.CharField(max_length=50, verbose_name='title', blank=True)),
                ('title_slug', models.SlugField(help_text=b'A "slug" is a unique URL-friendly title for an object.', verbose_name='slug', blank=True)),
                ('caption', models.TextField(null=True, verbose_name='caption', blank=True)),
                ('date_added', models.DateTimeField(default=datetime.datetime.now, verbose_name='date added', editable=False)),
                ('is_public', models.BooleanField(default=True, help_text='Public photographs will be displayed in the default views.', verbose_name='is public')),
                ('tags', photologue.models.TagField(help_text='Django-tagging was not found,         tags will be treated as plain text.', max_length=255, verbose_name='tags', blank=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['date_added'],
                'get_latest_by': 'date_added',
                'verbose_name': 'photo',
                'verbose_name_plural': 'photos',
            },
        ),
        migrations.CreateModel(
            name='PhotoEffect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30, verbose_name='name')),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('transpose_method', models.CharField(blank=True, max_length=15, verbose_name='rotate or flip', choices=[(b'FLIP_LEFT_RIGHT', 'Flip left to right'), (b'FLIP_TOP_BOTTOM', 'Flip top to bottom'), (b'ROTATE_90', 'Rotate 90 degrees counter-clockwise'), (b'ROTATE_270', 'Rotate 90 degrees clockwise'), (b'ROTATE_180', 'Rotate 180 degrees')])),
                ('color', models.FloatField(default=1.0, help_text='A factor of 0.0 gives a black and white image, a factor of 1.0 gives the original image.', verbose_name='color')),
                ('brightness', models.FloatField(default=1.0, help_text='A factor of 0.0 gives a black image, a factor of 1.0 gives the original image.', verbose_name='brightness')),
                ('contrast', models.FloatField(default=1.0, help_text='A factor of 0.0 gives a solid grey image, a factor of 1.0 gives the original image.', verbose_name='contrast')),
                ('sharpness', models.FloatField(default=1.0, help_text='A factor of 0.0 gives a blurred image, a factor of 1.0 gives the original image.', verbose_name='sharpness')),
                ('filters', models.CharField(help_text='Chain multiple filters using the following     pattern "FILTER_ONE->FILTER_TWO->FILTER_THREE". Image filters will     be applied in order. The following filters are available:     BLUR, CONTOUR, DETAIL, EDGE_ENHANCE, EDGE_ENHANCE_MORE, EMBOSS, FIND_EDGES, SHARPEN, SMOOTH, SMOOTH_MORE.', max_length=200, verbose_name='filters', blank=True)),
                ('reflection_size', models.FloatField(default=0, help_text='The height of the reflection as a percentage of the orignal image. A factor of 0.0 adds no reflection, a factor of 1.0 adds a reflection equal to the height of the orignal image.', verbose_name='size')),
                ('reflection_strength', models.FloatField(default=0.6, help_text='The initial opacity of the reflection gradient.', verbose_name='strength')),
                ('background_color', models.CharField(default=b'#FFFFFF', help_text='The background color of the reflection gradient. Set this to match the background color of your page.', max_length=7, verbose_name='color')),
            ],
            options={
                'verbose_name': 'photo effect',
                'verbose_name_plural': 'photo effects',
            },
        ),
        migrations.CreateModel(
            name='PhotoSize',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Photo size name should contain only letters, numbers and underscores. Examples: "thumbnail", "display", "small", "main_page_widget".', unique=True, max_length=40, verbose_name='name')),
                ('width', models.PositiveIntegerField(default=0, help_text='If width is set to "0" the image will be scaled to the supplied height.', verbose_name='width')),
                ('height', models.PositiveIntegerField(default=0, help_text='If height is set to "0" the image will be scaled to the supplied width', verbose_name='height')),
                ('quality', models.PositiveIntegerField(default=70, help_text='JPEG image quality.', verbose_name='quality', choices=[(30, 'Very Low'), (40, 'Low'), (50, 'Medium-Low'), (60, 'Medium'), (70, 'Medium-High'), (80, 'High'), (90, 'Very High')])),
                ('upscale', models.BooleanField(default=False, help_text='If selected the image will be scaled up if necessary to fit the supplied dimensions. Cropped sizes will be upscaled regardless of this setting.', verbose_name='upscale images?')),
                ('crop', models.BooleanField(default=False, help_text='If selected the image will be scaled and cropped to fit the supplied dimensions.', verbose_name='crop to fit?')),
                ('pre_cache', models.BooleanField(default=False, help_text='If selected this photo size will be pre-cached as photos are added.', verbose_name='pre-cache?')),
                ('increment_count', models.BooleanField(default=False, help_text='If selected the image\'s "view_count" will be incremented when this photo size is displayed.', verbose_name='increment view count?')),
                ('effect', models.ForeignKey(related_name='photo_sizes', verbose_name='photo effect', blank=True, to='photologue.PhotoEffect', null=True)),
            ],
            options={
                'ordering': ['width', 'height'],
                'verbose_name': 'photo size',
                'verbose_name_plural': 'photo sizes',
            },
        ),
        migrations.CreateModel(
            name='Watermark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30, verbose_name='name')),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('image', models.ImageField(upload_to=b'/watermarks', verbose_name='image')),
                ('style', models.CharField(default=b'scale', max_length=5, verbose_name='style', choices=[(b'tile', 'Tile'), (b'scale', 'Scale')])),
                ('opacity', models.FloatField(default=1, help_text='The opacity of the overlay.', verbose_name='opacity')),
            ],
            options={
                'verbose_name': 'watermark',
                'verbose_name_plural': 'watermarks',
            },
        ),
        migrations.AddField(
            model_name='photosize',
            name='watermark',
            field=models.ForeignKey(related_name='photo_sizes', verbose_name='watermark image', blank=True, to='photologue.Watermark', null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='effect',
            field=models.ForeignKey(related_name='photo_related', verbose_name='effect', blank=True, to='photologue.PhotoEffect', null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='gallery',
            field=models.ForeignKey(related_name='photos', to='photologue.Gallery'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='featured_photo',
            field=models.ForeignKey(related_name='gallery_', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='photologue.Photo', help_text=b'The featured photo is the symbol for the gallery.', null=True),
        ),
    ]
