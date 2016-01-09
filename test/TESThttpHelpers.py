import os,sys,inspect
##currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
##parentdir = os.path.dirname(currentdir)
sys.path.insert(0,"..") 

import unittest
from httpHelpers import *

# Here's our "unit tests".
class openURLTests(unittest.TestCase):

    def testOne(self):
		google = openUrl("https://www.google.com")
		testString = google.read()[:15]
		self.failUnless(testString == "<!doctype html>")

def main():
    unittest.main()

if __name__ == '__main__':
    main()