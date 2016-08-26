#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import weather


class WeatherTestCase(unittest.TestCase):

    def setUp(self):
        weather.app.config['TESTING'] = True
        self.app = weather.app.test_client()

    def tearDown(self):
        pass

    def test_health(self):
        rv = self.app.get('/healthz')
        assert b'ok' in rv.data

    def test_is_metric(self):
        weather.TEMP_SCALE = "C"
        self.assertTrue(weather.is_metric())
        weather.TEMP_SCALE = "F"
        self.assertFalse(weather.is_metric())

    def test_convert_to_dict(self):
        with open("fixtures/weather.json") as fp:
            response = fp.read()
        expected = dict(
            city="Beijing",
            country="CN",
            temp=13.39,
            format="Celsius")
        self.assertDictEqual(expected, weather.convert_to_dict(response))


if __name__ == '__main__':
    unittest.main()
