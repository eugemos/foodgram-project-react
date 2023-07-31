from core.tests.base import (
    EndpointTestCase, TestSimpleListMixin, TestSimpleDetailMixin, TestTag
)


class TagEndpointTestCase(EndpointTestCase, TestTag):
    BASE_URL = '/api/tags/'


class TagListTestCase(TestSimpleListMixin, TagEndpointTestCase):
    pass


class TagDetailTestCase(TestSimpleDetailMixin, TagEndpointTestCase):
    pass
