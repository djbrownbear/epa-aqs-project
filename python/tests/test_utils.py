import unittest
import json
import os
from utils import mask_api_key_and_email, format_date_to_yyyymmdd, save_json_to_file, load_json_to_dataframe

class TestUtils(unittest.TestCase):
    def test_mask_api_key_and_email(self):
        data = {
            "Header": [
                {
                    "url": "https://example.com?email=test@example.com&key=12345"
                }
            ]
        }
        expected = {
            "Header": [
                {
                    "url": "https://example.com?email=*****&key=*****"
                }
            ]
        }
        self.assertEqual(mask_api_key_and_email(data), expected)

    def test_format_date_to_yyyymmdd(self):
        self.assertEqual(format_date_to_yyyymmdd("2025-09-06"), "20250906")
        self.assertEqual(format_date_to_yyyymmdd("09-06-2025"), "20250906")
        self.assertEqual(format_date_to_yyyymmdd("2025/09/06"), "20250906")
        self.assertEqual(format_date_to_yyyymmdd("09/06/2025"), "20250906")

        with self.assertRaises(ValueError):
            format_date_to_yyyymmdd("invalid-date")

    def test_save_json_to_file(self):
        data = {"key": "value"}
        file_path = "test.json"
        save_json_to_file(data, file_path)

        with open(file_path, "r") as file:
            loaded_data = json.load(file)

        self.assertEqual(data, loaded_data)
        os.remove(file_path)  # Clean up the test file

    def test_load_json_to_dataframe(self):
        data = {
            "Data": [
                {"column1": "value1", "column2": "value2"},
                {"column1": "value3", "column2": "value4"}
            ]
        }
        file_path = "test.json"
        save_json_to_file(data, file_path)

        df = load_json_to_dataframe(record_path="Data", filename=file_path)

        self.assertEqual(len(df), 2)
        self.assertListEqual(list(df.columns), ["column1", "column2"])
        os.remove(file_path)  # Clean up the test file

if __name__ == "__main__":
    unittest.main()
