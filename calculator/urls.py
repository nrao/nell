from django.conf.urls.defaults import *

urlpatterns = patterns('calculator.views',
    (r'^set_terms/$',  'set_terms'),
    (r'^get_results$', 'get_results'),
    (r'^initiate_hardware$','initiateHardware'),
    (r'^set_hardware$','setHardware'),
    (r'^results$','display_results'),
)
