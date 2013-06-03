#!/usr/bin/env python
# -*- coding: utf-8 -*-
from photologue.models import Photo, Gallery
from photologue.forms import GalleryForm, GalleryPhotoForm

from django.views.generic.dates import ArchiveIndexView, DateDetailView, DayArchiveView, MonthArchiveView, YearArchiveView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.template.defaultfilters import slugify
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType


def upload_photo(request, gallery_id):
    gallery = get_object_or_404(Gallery, pk=gallery_id)
    if request.method == 'POST':
        form = GalleryPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.author = request.user
            photo.title_slug = slugify(photo.title)
            photo.is_public = True
            photo.save()
            # Following was implemented to add photos recursively to parent galleries... Being phased out in favor of Gallery "children_photos()" method
            #  content_type = ContentType.objects.get(pk=gallery.content_type_id)
             # if content_type.model == 'narrative':
            #     for explorer in gallery.narrative.experience.explorers.all():
            #         explorer.gallery.photos.add(photo)
            #     gallery.photos.add(photo)
            #     gallery.narrative.experience.gallery.photos.add(photo)
            #     gallery.photos.add(photo)
            # elif content_type.model == 'experience':
            #     for explorer in gallery.experience.explorers.all():
            #         explorer.gallery.photos.add(photo)
            #     gallery.photos.add(photo)
            # elif content_type.model == 'explorer':
            #     for explorer in gallery.explorers.all():
            #         explorer.gallery.photos.add(photo)
            if 'feature' in request.POST.keys():
                gallery.featured_photo = photo
                gallery.save()
            gallery.photos.add(photo)
            messages.success(request, 'Your photo was successfully uploaded')
            return HttpResponseRedirect('/photologue/gallery/{0}/'.format(gallery.id))
    else:
        form = GalleryPhotoForm()
    return render(request, 'photologue/upload_photo.html', {'form': form, 'gallery': gallery})


def edit_photo(request, photo_id):
    # return HttpResponse('Thought this wasn\'t needed')
    photo = get_object_or_404(Photo, pk=photo_id)
    if request.method == 'POST':
        for field in request.POST:
            setattr(photo, field, request.POST[field])
        photo.save()
        messages.success(request, 'Your photo was updated')
        return redirect('/photologue/photo/{0}'.format(photo.id))
    else:
        form = GalleryPhotoForm(instance=photo)
    return render(request, 'photologue/gallery_edit.html', {'form': form})


def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    galleries = [g for g in photo.public_galleries()]
    if request.method == 'POST':
        photo.delete()
    return redirect(reverse('pl-gallery', args=(galleries[0].id,)))


class PhotoView(object):
    queryset = Photo.objects.all()  # filter(is_public=True)


class PhotoListView(PhotoView, ListView):
    paginate_by = 20


class PhotoDetailView(PhotoView, DetailView):
    slug_field = 'title_slug'


class PhotoDateView(PhotoView):
    date_field = 'date_added'


class PhotoDateDetailView(PhotoDateView, DateDetailView):
    slug_field = 'title_slug'


class PhotoArchiveIndexView(PhotoDateView, ArchiveIndexView):
    pass


class PhotoDayArchiveView(PhotoDateView, DayArchiveView):
    pass


class PhotoMonthArchiveView(PhotoDateView, MonthArchiveView):
    pass


class PhotoYearArchiveView(PhotoDateView, YearArchiveView):
    pass


#gallery Views
def gallery_view(request, pk):
    gallery = get_object_or_404(Gallery, pk=pk)
    children_photos = gallery.children_photos()
    return render(request, 'photologue/gallery_detail.html', {'children_photos': children_photos, 'object': gallery})


def gallery_edit(request, gallery_id):
    gallery = get_object_or_404(Gallery, pk=gallery_id)
    if request.user in gallery.explorers.all():
        if request.method == 'POST':
            for field in request.POST:
                if field == 'featured_photo':
                    setattr(gallery, field, Photo.objects.get(pk=request.POST[field]))
                else:
                    setattr(gallery, field, request.POST[field])
            gallery.save()
            messages.success(request, 'Gallery has been updated')
            return redirect('/photologue/gallery/{0}'.format(gallery_id))
        photos = gallery.photos.all()
        photos_forms = []
        for photo in photos:
            form = GalleryPhotoForm(instance=photo)
            photos_forms.append((photo, form))
        form = GalleryForm(gallery=gallery, instance=gallery)
        return render(request, 'photologue/gallery_edit.html', {'object': gallery, 'form': form, 'photos_forms': photos_forms})
    else:
        messages.error(request, 'Nice try on security breach! I would, however, love it if you did inform me of a website security weakness should (when) you find one.')
        return render(request, 'acressity/message.html')


# def edit_gallery(request, gallery_id):
#     gallery = get_object_or_404(Gallery, pk=gallery_id)
#     else:
#         form = GalleryForm(instance=gallery)
#     return render(request, 'photologue/gallery_edit.html', {'form': form})


class GalleryView(object):
    queryset = Gallery.objects.filter(is_public=True)


class GalleryListView(GalleryView, ListView):
    paginate_by = 20


class GalleryDetailView(GalleryView, DetailView):
    slug_field = 'title_slug'


class GalleryDateView(GalleryView):
    date_field = 'date_added'


class GalleryDateDetailView(GalleryDateView, DateDetailView):
    slug_field = 'title_slug'


class GalleryArchiveIndexView(GalleryDateView, ArchiveIndexView):
    pass


class GalleryDayArchiveView(GalleryDateView, DayArchiveView):
    pass


class GalleryMonthArchiveView(GalleryDateView, MonthArchiveView):
    pass


class GalleryYearArchiveView(GalleryDateView, YearArchiveView):
    pass
