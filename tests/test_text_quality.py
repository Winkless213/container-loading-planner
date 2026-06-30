import unittest

import text_quality


class TextQualityTest(unittest.TestCase):
    def test_project_text_has_no_common_mojibake(self):
        self.assertEqual([], text_quality.check_project_text())

    def test_detector_flags_utf8_decoded_as_gbk(self):
        broken = "\u88c5\u67dc".encode("utf-8").decode("gbk")

        issues = text_quality.find_mojibake_in_text("sample", broken)

        self.assertEqual(1, len(issues))
        self.assertEqual("sample", issues[0].path)


if __name__ == "__main__":
    unittest.main()
