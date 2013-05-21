from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'crowd_lookup.views.index'),

    url(r'^lookup/recomm/get/$', 'crowd_lookup.views.get_recomm'),
    url(r'^lookup/recomm/delete/$', 'crowd_lookup.views.delete_recomm'),
    url(r'^lookup/explain/query/$', 'crowd_lookup.views.query_explain'),
    url(r'^lookup/explain/delete/$', 'crowd_lookup.views.delete_explain'),
    url(r'^lookup/explain/provide/$', 'crowd_lookup.views.provide_explain'),

    # Examples:
    # url(r'^$', 'nine_gag_wrapper.views.home', name='home'),
    # url(r'^nine_gag_wrapper/', include('nine_gag_wrapper.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
