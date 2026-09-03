from django.test import TestCase

from intelligence.serializers import TickerSerializer


class TickerSerializerTests(TestCase):
    def test_symbol_is_uppercased(self):
        serializer = TickerSerializer(data={"symbol": "aapl", "company_name": "Apple"})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["symbol"], "AAPL")
