from django.test import TestCase, Client

# Create your tests here.

class BasicTestCase(TestCase):
    def setUp(self):
        pass

    def test_view_health_check(self):
        c = Client()
        response = c.get('/af/')
        self.assertEqual(response.status_code, 200)

    def test_view(self):
        c = Client()
        response = c.get('/af/')
        self.assertEqual(response.context['plot_div'], '')
