# -*- coding: utf-8 -*-

from django import test
from django.conf import settings
import selectreverse.tests.models as test_models
from django.db import connection,  reset_queries
from django.core.exceptions import ImproperlyConfigured
from django.template import Context, Template

class Test_m2m(test.TestCase):
    def setUp(self):
        settings.DEBUG = True

        for i in range(10):
            o = test_models.Owner(name='Joe')
            o.save()

        for i in range(20):
            a = test_models.Building(number= i)
            a.save()
            a.owners.add(o)

            for j in range(5):
                b = test_models.Apartment(building=a,   number = i*10+j)
                b.save()
                c = test_models.Parking(building=a,  number=i*10+j)
                c.save()

    def test_config(self):
        def testfunc():
            for x in test_models.Building.reversemanager.select_reverse({'owners': 'owners'}):
                pass

        self.assertRaises(ImproperlyConfigured, testfunc)

    def test_reverseFK(self):
        reset_queries()
        for item in test_models.Building.objects.all():
            for x in item.apartment_set.all():
                a = x.number
            for x in item.parking_set.all():
                a = x.number
        self.assertEqual(len(connection.queries), 41)

        reset_queries()
        # all includes all default mappings, as defined in the manager initialisation
        for item in test_models.Building.reversemanager.all():
            for x in getattr(item,  'apartments'):
                a = x.number
            for x in getattr(item,  'parkings'):
                a = x.number
        self.assertEqual(len(connection.queries), 4)

        reset_queries()
        for item in test_models.Building.reversemanager.select_reverse({'apartments': 'apartment_set'}):
            for x in getattr(item,  'apartments'):
                a = x.number
        self.assertEqual(len(connection.queries), 2)

        reset_queries()
        for item in test_models.Building.reversemanager.select_reverse({'parkings': 'parking_set'}):
            for x in getattr(item,  'parkings'):
                a = x.number
        self.assertEqual(len(connection.queries), 2)

	# test select_reverse works on a filtered set
        reset_queries()
        for item in test_models.Building.reversemanager.filter(number__lt = 5).select_reverse({'parkings': 'parking_set'}):
            for x in getattr(item,  'parkings'):
                a = x.number
        self.assertEqual(len(connection.queries), 2)

    def test_m2m(self):
        reset_queries()
        for item in test_models.Building.objects.all():
            for x in item.owners.all():
                a = x.name
        self.assertEqual(len(connection.queries), 21)

        reset_queries()
        # all includes all default mappings, as defined in the manager initialisation
        for item in test_models.Building.reversemanager.all():
            for x in getattr(item,  'xowners'):
                a = x.name
        self.assertEqual(len(connection.queries), 4)

        reset_queries()
        for item in test_models.Building.reversemanager.select_reverse({'xowners': 'owners'}):
            for x in getattr(item,  'xowners'):
                a = x.name
        self.assertEqual(len(connection.queries), 2)

	# test select_reverse works on a filtered set
        reset_queries()
        for item in test_models.Building.reversemanager.filter(number__lt = 5).select_reverse({'xowners': 'owners'}):
            for x in getattr(item,  'xowners'):
                a = x.name
        self.assertEqual(len(connection.queries), 2)

    def test_reversem2m(self):
        reset_queries()
        for item in test_models.Owner.objects.all():
            for x in item.building_set.all():
                a = x.number
        self.assertEqual(len(connection.queries), 11)

        reset_queries()
        # all includes all default mappings, as defined in the manager initialisation
        for item in test_models.Owner.reversemanager.all():
            for x in getattr(item,  'buildings'):
                a = x.number
        self.assertEqual(len(connection.queries), 2)

        reset_queries()
        for item in test_models.Owner.reversemanager.select_reverse({'buildings': 'building_set'}):
            for x in getattr(item,  'buildings'):
                a = x.number
        self.assertEqual(len(connection.queries), 2)

	# test select_reverse works on a filtered set
        reset_queries()
        for item in test_models.Owner.reversemanager.filter(pk__lt = 5).select_reverse({'buildings': 'building_set'}):
            for x in getattr(item,  'buildings'):
                a = x.number
        self.assertEqual(len(connection.queries), 2)

    # you can filter further on a set with select_reverse defined
        reset_queries()
        for item in test_models.Owner.reversemanager.select_reverse({'buildings': 'building_set'}).filter(pk__lt = 5):
            for x in getattr(item,  'buildings'):
                a = x.number
        self.assertEqual(len(connection.queries), 2)

class Test_generic(test.TestCase):
    def setUp(self):
        settings.DEBUG = True

        for i in range(10):
            o = test_models.Bookmark(url='http://www.djangoproject.com/')
            o.save()
            for i in range(20):
                a = test_models.TaggedItem(content_object=o, tag= str(i))
                a.save()

    def test_reverseGFK(self):
        reset_queries()
        for item in test_models.Bookmark.objects.all():
            for x in item.tags.all():
                a = x.tag
        self.assertEqual(len(connection.queries), 11)

        reset_queries()
        # all includes all default mappings, as defined in the manager initialisation
        for item in test_models.Bookmark.reversemanager.all():
            for x in getattr(item,  'gtags'):
                a = x.tag
        self.assertEqual(len(connection.queries), 2)

class Test_template(Test_m2m):
    def test_template(self):
        reset_queries()
        d = {'buildings': test_models.Building.reversemanager.select_reverse({'apartments': 'apartment_set'})}
        t = Template("{% for item in buildings %}{% for apartment in item.apartments %}{{ apartment }}{% endfor %}{% endfor %}")
        response = t.render(Context(d))
        self.assertEqual(len(response), 245)
        self.assertEqual(len(connection.queries), 2)
    
