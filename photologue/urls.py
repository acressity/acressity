from django.conf.urls.defaults import *
from photologue.views import PhotoListView, PhotoDetailView, GalleryListView, \
    GalleryDetailView, PhotoArchiveIndexView, PhotoDateDetailView, PhotoDayArchiveView, \
    PhotoYearArchiveView, PhotoMonthArchiveView, GalleryArchiveIndexView, \
    GalleryYearArchiveView, GalleryDateDetailView, GalleryDayArchiveView, \
    GalleryMonthArchiveView

urlpatterns = patterns(
    '',
    url(r'^gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$',
        GalleryDateDetailView.as_view(),
        name='pl-gallery-detail'),
    url(r'^gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',
        GalleryDayArchiveView.as_view(),
        name='pl-gallery-archive-day'),
    url(r'^gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
        GalleryMonthArchiveView.as_view(),
        name='pl-gallery-archive-month'),
    url(r'^gallery/(?P<year>\d{4})/$',
        GalleryYearArchiveView.as_view(),
        name='pl-gallery-archive-year'),
    url(r'^gallery/$',
        GalleryArchiveIndexView.as_view(),
        name='pl-gallery-archive'),
    url(r'^gallery/(?P<gallery_id>\d+)/gallery_edit/$', 'photologue.views.gallery_edit', name='pl-gallery-edit'),
    # url(r'^gallery/(?P<gallery_id>\d+)/edit_gallery/$', 'photologue.views.edit_gallery'),
    url(r'^gallery/(?P<gallery_id>\d+)/upload_photo/$', 'photologue.views.upload_photo'),
    # Following was photologue written url:
    # url(r'^gallery/(?P<pk>[\-\d\w]+)/$', GalleryDetailView.as_view(), name='pl-gallery'),
    # Following is user generated to alter behavior:
    url(r'^gallery/(?P<pk>[\-\d\w]+)/$', 'photologue.views.gallery_view', name='pl-gallery'),
    url(r'^gallery/page/(?P<page>[0-9]+)/$', GalleryListView.as_view(), name='pl-gallery-list'),

    # Following was the original:
    # url(r'^gallery/page/(?P<page>[0-9]+)/$', GalleryListView.as_view(), name='pl-gallery-list'),

    url(r'^photo/(?P<photo_id>\d+)/edit_photo/$', 'photologue.views.edit_photo'),
    url(r'^photo/(?P<photo_id>\d+)/delete_photo/$', 'photologue.views.delete_photo'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$',
        PhotoDateDetailView.as_view(),
        name='pl-photo-detail'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',
        PhotoDayArchiveView.as_view(),
        name='pl-photo-archive-day'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
        PhotoMonthArchiveView.as_view(),
        name='pl-photo-archive-month'),
    # url(r'^photo/(?P<year>\d{4})/$',
    #     PhotoYearArchiveView.as_view(),
    #     name='pl-photo-archive-year'),
    url(r'^photo/$',
        PhotoArchiveIndexView.as_view(),
        name='pl-photo-archive'),

    url(r'^photo/(?P<pk>[\-\d\w]+)/$',
        PhotoDetailView.as_view(),
        name='pl-photo'),
    url(r'^photo/page/(?P<page>[0-9]+)/$',
        PhotoListView.as_view(),
        name='pl-photo-list'),

)