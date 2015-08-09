from django.forms import ModelForm, extras
from django.contrib.contenttypes.models import ContentType

from photologue.models import Photo, Gallery
from django import forms


class GalleryPhotoForm(ModelForm):
    class Meta:
        model = Photo
        exclude = ('title_slug', 'author', 'gallery')


class GalleryForm(ModelForm):
    date_added = forms.DateField(widget=forms.extras.widgets.SelectDateWidget())

    def __init__(self, gallery, *args, **kwargs):
        # initial = {'experience': ''}
        super(GalleryForm, self).__init__(*args, **kwargs)
        if self.instance.content_type == ContentType.objects.get(name='Narrative'):
            self.fields['featured_photo'].queryset = gallery.photos.all()
        else:
            self.fields['featured_photo'].queryset = gallery.children_photos() | gallery.photos.all()

    class Meta:
        model = Gallery
        exclude = ()
