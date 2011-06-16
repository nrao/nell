from django.test.client  import Client
from django.conf         import settings
from django.contrib.auth import models as m
import unittest

class TestViewsBase(unittest.TestCase):

    def setUp(self):

        # Don't use CAS for authentication during unit tests
        if 'django_cas.backends.CASBackend' in settings.AUTHENTICATION_BACKENDS:
            settings.AUTHENTICATION_BACKENDS = settings.AUTHENTICATION_BACKENDS[:-1]
        if 'django_cas.middleware.CASMiddleware' in settings.MIDDLEWARE_CLASSES:
            settings.MIDDLEWARE_CLASSES      = settings.MIDDLEWARE_CLASSES[:-1]

        self.client = Client()

        self.auth_user = m.User.objects.create_user('dss', 'dss@nrao.edu', 'asdf5!')
        self.auth_user.save()
        r = self.client.login(username = "dss", password = "asdf5!")

    def tearDown(self):
        self.auth_user.delete()
