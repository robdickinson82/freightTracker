import os,sys,inspect
##currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
##parentdir = os.path.dirname(currentdir)
sys.path.insert(0,"..") 

import unittest
from main import *

# Here's our "unit tests".
class mainTests(unittest.TestCase):

    def testOne(self):
		html = openRTTUrl_CMDNRDJ_AroundNow()
		hasResultsTable = html.find("table table-condensed servicelist advanced")
		self.failIf(hasResultsTable == -1)

def main():
    unittest.main()

if __name__ == '__main__':
    main()