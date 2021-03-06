#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from django.views.generic.dates import ArchiveIndexView, DateDetailView, DayArchiveView, MonthArchiveView, YearArchiveView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.template.defaultfilters import slugify
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string

from acressity import settings
from photologue.models import Photo, Gallery
from photologue.forms import GalleryForm, GalleryPhotoForm
from notifications import notify


def upload_photo(request, gallery_id):
    gallery = get_object_or_404(Gallery, pk=gallery_id)
    if request.method == 'POST':
        form = GalleryPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.author = request.user
            photo.title_slug = slugify(photo.title)
            photo.is_public = True
            photo.gallery = gallery
            photo.save()
            if 'feature' in request.POST.keys():
                gallery.featured_photo = photo
                gallery.save()
            messages.success(request, 'Your photo was successfully uploaded')
            for comrade in gallery.explorers.exclude(id=request.user.id):
                notify.send(sender=request.user, recipient=comrade, target=photo, verb='has uploaded a new photo')
            return HttpResponseRedirect('/photologue/gallery/{0}/'.format(gallery.id))
    else:
        form = GalleryPhotoForm()
    return render(request, 'photologue/upload_photo.html', {'form': form, 'gallery': gallery})


def ajax_upload(request):
    gallery = get_object_or_404(Gallery, pk=request.POST.get('gallery_id'))
    assert request.user in gallery.explorers.all()
    if request.method == 'POST':
        form = GalleryPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.author = request.user
            photo.title_slug = slugify(photo.title)
            photo.is_public = True
            photo.gallery = gallery
            photo.save()
            if 'feature' in request.POST.keys():
                gallery.featured_photo = photo
                gallery.save()
            for comrade in gallery.explorers.exclude(id=request.user.id):
                notify.send(sender=request.user, recipient=comrade, target=photo, verb='has uploaded a new photo')
            data = {'html': render_to_string('photologue/snippets/photo_dash.html', {'photo': photo, 'user': request.user, 'STATIC_URL': settings.STATIC_URL })}
            return HttpResponse(json.dumps(data))
        else:
            # Here's the problem with the images not uploading properly
            return HttpResponse('Please fill out the form correctly')
    # Return nothing for failure??
    return HttpResponse('api')


@login_required
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


@login_required
def update_photo(request):
    photo = Photo.objects.get(pk=request.GET.get('photo_id'))
    photo.title = request.GET.get('title')
    photo.caption = request.GET.get('caption')
    d = {}
    try:
        photo.save()
    except:
        d['yack'] = 'There was a failure saving your photo'
    else:
        d['yack'] = 'Your photo has been saved successfully'
    json_response = json.dumps(d)
    return HttpResponse(json_response)


@login_required
def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    if request.user == photo.author:
        photo.delete()
        messages.success(request, 'Photo was successfully deleted')
    else:
        raise PermissionDenied
    return redirect(reverse('pl-gallery-edit', args=(photo.gallery.id,)))


def photo_view(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    # I'm not sure this is the best thing...
    if not photo.gallery.is_public:
        if request.user not in photo.gallery.explorers.all():
            raise PermissionDenied
    return render(request, 'photologue/photo_detail.html', {'object': photo})


class PhotoView(object):
    queryset = Photo.objects.filter(is_public=True)


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


# Gallery views
def gallery_view(request, pk):
    gallery = get_object_or_404(Gallery, pk=pk)
    photos_per_page = 25
    if not gallery.is_public and request.user not in gallery.explorers.all():
        raise PermissionDenied
    paginator = Paginator(gallery.photos.reverse(), photos_per_page)
    page = request.GET.get('page')
    try: 
        photos = paginator.page(page)
    except PageNotAnInteger:
        # Deliver the first page
        photos = paginator.page(1)
    except:
        # Deliver last page
        photos = paginator.page(paginator.num_pages)
    return render(request, 'photologue/gallery_detail.html', {'photos': photos,
        'object': gallery, 'is_paginated': paginator.num_pages > 1})


@login_required
def gallery_edit(request, gallery_id):
    gallery = get_object_or_404(Gallery, pk=gallery_id)
    if request.user in gallery.explorers.all():
        if request.method == 'POST':
            for field in request.POST:
                if field == 'featured_photo':
                    if request.POST[field]:
                        photo = Photo.objects.get(pk=request.POST.get(field))
                        if photo not in gallery.photos.all():
                            raise PermissionDenied
                        setattr(gallery, field, photo)
                    else:
                        setattr(gallery, field, None)
                else:
                    setattr(gallery, field, request.POST.get(field))
            gallery.save()
            messages.success(request, 'Gallery has been updated')
            return redirect('/photologue/gallery/{0}'.format(gallery_id))
        photos = gallery.photos.all()
        photos_forms = []
        for photo in photos:
            form = GalleryPhotoForm(instance=photo)
            photos_forms.append((photo, form))
        form = GalleryForm(gallery=gallery, instance=gallery)
        return render(request, 'photologue/gallery_edit.html', {'object':
            gallery, 'form': form, 'photos_forms': photos_forms})
    else:
        raise PermissionDenied


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
