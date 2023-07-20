from django.test import TestCase
from django.db.utils import IntegrityError

from api.models import Tag


class TestTagModelCase(TestCase):
    def create_test_tag(self):
        Tag.objects.create(name='TestTag', color='#123456', slug='test-tag')

    def test_correct_tag_created(self):
        self.assertEqual(Tag.objects.count(), 0)
        self.create_test_tag()
        self.assertEqual(Tag.objects.count(), 1)

    def test_unique_constraints_work_properly(self):
        self.assertEqual(Tag.objects.count(), 0, '1')
        self.create_test_tag()
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name='TestTag', color='#111222', slug='another-test-tag')
        # self.assertEqual(Tag.objects.count(), 0, '2')

    def test_incorrect_tag_not_created(self):
        self.assertEqual(Tag.objects.count(), 0, '1')
        Tag.objects.create(name='TestTag', )
        self.assertEqual(Tag.objects.count(), 0, '2')
