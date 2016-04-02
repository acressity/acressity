from django import forms
from django.forms import ModelForm
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from photologue.models import Photo, Gallery
from narratives.models import Narrative


class GalleryPhotoForm(ModelForm):
    class Meta:
        model = Photo
        exclude = ('title_slug', 'author', 'gallery')

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            title = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        return title


class GalleryForm(ModelForm):
    date_added = forms.DateField(widget=forms.extras.widgets.SelectDateWidget())

    def __init__(self, gallery, *args, **kwargs):
        # initial = {'experience': ''}
        super(GalleryForm, self).__init__(*args, **kwargs)
        if self.instance.content_type == ContentType.objects.get_for_model(Narrative):
            self.fields['featured_photo'].queryset = gallery.photos.all()
        else:
            self.fields['featured_photo'].queryset = gallery.children_photos() | gallery.photos.all()

    class Meta:
        model = Gallery
        exclude = ()
