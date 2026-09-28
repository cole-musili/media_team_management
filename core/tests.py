from django.test import TestCase
from django.urls import reverse
class DashboardTest(TestCase):
    def test_dashboard_loads(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
