import os
import unittest
from app import app
from flask import json


class AppCase(unittest.TestCase):
    def test_detect_gender_and_age(self):
        response = app.test_client().post(
            '/api/v1/detect-gender-and-age',
            data={
                'image': (os.path.join(f"./fixtures/putin.jpg"), "img.jpg")
            },
            content_type='multipart/form-data',
        )

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.get_data(as_text=True))

        self.assertEqual('image' in body, True)


if __name__ == '__main__':
    unittest.main()
