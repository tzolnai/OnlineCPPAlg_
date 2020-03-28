import sys
import os
# Add the local path to the main script so we can import them.
sys.path = [".."] + sys.path

import unittest
import OnlineCPPAlg as ocpp

class graphValidationTest(unittest.TestCase):

	def testAllNodesVisited(self):
		alg = ocpp.OnlineCPPAlg()
		alg.run()
		for node in alg.graph.getNodeDict():
			self.assertTrue(alg.graph.getNodeDict()[node]['visited'])

	def testAllNodesPartOfTheTree(self):
		alg = ocpp.OnlineCPPAlg()
		alg.run()

		for node in alg.graph.getNodeDict():
			print(node)
			found = False
			for edge in alg.graph.getEdges():
				if edge[0] == node or edge[1] == node:
					found = True
					break
			self.assertTrue(found)

	def testAllNodesHaveOneParent(self):
		alg = ocpp.OnlineCPPAlg()
		alg.run()

		for node in alg.graph.getNodeDict():
			print(node)
			parent_count = 0
			for edge in alg.graph.getEdges():
				if edge[1] == node:
					parent_count += 1
			if node == (0,0):
				self.assertEqual(parent_count, 0)
			else:
				self.assertEqual(parent_count, 1)

	def testAllNodesChildNumber(self):
		alg = ocpp.OnlineCPPAlg()
		alg.run()

		for node in alg.graph.getNodeDict():
			print(node)
			child_count = 0
			for edge in alg.graph.getEdges():
				if edge[0] == node:
					child_count += 1
			assert(child_count <= 4)

	def testGraphCoversEnvironment(self):
		alg = ocpp.OnlineCPPAlg()
		alg.run()

		for free_cell in alg.environment.getAllFreeCells():
			assert(free_cell in alg.graph.getNodeDict())


if __name__ == "__main__":
    unittest.main()  # run all tests