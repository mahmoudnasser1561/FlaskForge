import unittest


class CIVerifyBrokenTestCase(unittest.TestCase):
    def test_deliberately_fails(self):
        self.assertTrue(False, "deliberate failure to verify CI reports red")
