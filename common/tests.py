from django.test import TestCase, Client

# Create your tests here.


class BasicTestCase(TestCase):
    def setUp(self):
        pass

    def test_views_health_check(self):
        c = Client()
        response = c.get('/')
        self.assertEqual(response.status_code, 200)
        response = c.get('/about')
        self.assertEqual(response.status_code, 200)
        response = c.get('/support')
        self.assertEqual(response.status_code, 200)
