from django.forms import ModelForm, extras
from photologue.models import Photo, Gallery
from django import forms


class GalleryPhotoForm(ModelForm):
    class Meta:
        model = Photo
        exclude = ('title_slug', 'author')


class GalleryForm(ModelForm):
    date_added = forms.DateField(widget=forms.extras.widgets.SelectDateWidget())

    def __init__(self, gallery, *args, **kwargs):
        # initial = {'experience': ''}
        super(GalleryForm, self).__init__(*args, **kwargs)
        self.fields['featured_photo'].queryset = gallery.children_photos()

    class Meta:
        model = Gallery
