from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'crowd_lookup.views.index'),

    url(r'^lookup/recomm/(?P<gag_id>\d+)$', 'crowd_lookup.views.get_recomm_words'),
    url(r'^lookup/query/$', 'crowd_lookup.views.query_word'),

    # Examples:
    # url(r'^$', 'nine_gag_wrapper.views.home', name='home'),
    # url(r'^nine_gag_wrapper/', include('nine_gag_wrapper.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
