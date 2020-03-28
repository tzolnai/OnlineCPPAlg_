import sys
import os
# Add the local path to the main script so we can import them.
sys.path = [".."] + sys.path

import unittest
import OnlineCPPAlg as ocpp

class validationTest(unittest.TestCase):

	def testOutputGraphValidity(self):
		alg = ocpp.OnlineCPPAlg()
		alg.run()		
		for node in alg.graph.getNodeDict():
			self.assertEqual(alg.graph.getNodeDict()[node]['visited'], True)

if __name__ == "__main__":
    unittest.main()  # run all tests