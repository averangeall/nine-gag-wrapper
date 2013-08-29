from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'crowd_lookup.views.index'),
    url(r'^test/$', 'crowd_lookup.views.test'),

    url(r'^lookup/user/new/$', 'crowd_lookup.views.new_user'),
    url(r'^lookup/user/rename/$', 'crowd_lookup.views.rename_user'),
    url(r'^lookup/user/info/$', 'crowd_lookup.views.info_user'),

    url(r'^lookup/recomm/get/$', 'crowd_lookup.views.get_recomm'),
    url(r'^lookup/recomm/hate/$', 'crowd_lookup.views.hate_recomm'),
    url(r'^lookup/recomm/id/$', 'crowd_lookup.views.id_recomm'),

    url(r'^lookup/explain/query/$', 'crowd_lookup.views.query_explain'),
    url(r'^lookup/explain/hate/$', 'crowd_lookup.views.hate_explain'),
    url(r'^lookup/explain/like/$', 'crowd_lookup.views.like_explain'),
    url(r'^lookup/explain/neutral/$', 'crowd_lookup.views.neutral_explain'),
    url(r'^lookup/explain/provide/$', 'crowd_lookup.views.provide_explain'),

    url(r'^lookup/image/avatar/$', 'crowd_lookup.views.avatar_image'),
    url(r'^lookup/image/treasure/$', 'crowd_lookup.views.treasure_image'),

    url(r'^lookup/treasure/buy/$', 'crowd_lookup.views.buy_treasure'),
    url(r'^lookup/treasure/use/$', 'crowd_lookup.views.use_treasure'),
    url(r'^lookup/treasure/info/$', 'crowd_lookup.views.info_treasure'),

    # Examples:
    # url(r'^$', 'nine_gag_wrapper.views.home', name='home'),
    # url(r'^nine_gag_wrapper/', include('nine_gag_wrapper.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
