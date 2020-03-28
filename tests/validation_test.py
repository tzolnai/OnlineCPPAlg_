import sys
import os
# Add the local path to the main script so we can import them.
sys.path = [".."] + sys.path

import unittest
import OnlineCPPAlg as ocpp

class graphValidationTest(unittest.TestCase):

	def runAlgorithm(self):
		charging_station = (0,0)
		environment = ocpp.Environment(4, 5, charging_station, [(2,1), (3,1), (2,2), (3,2)])
		energy_budget = 20
		self.alg = ocpp.OnlineCPPAlg(charging_station, environment, energy_budget)
		self.alg.run()

	def testAllNodesVisited(self):
		self.runAlgorithm()

		for node in self.alg.graph.getNodeDict():
			self.assertTrue(self.alg.graph.getNodeDict()[node]['visited'])

	def testAllNodesPartOfTheTree(self):
		self.runAlgorithm()

		for node in self.alg.graph.getNodeDict():
			print(node)
			found = False
			for edge in self.alg.graph.getEdges():
				if edge[0] == node or edge[1] == node:
					found = True
					break
			self.assertTrue(found)

	def testAllNodesHaveOneParent(self):
		self.runAlgorithm()


		for node in self.alg.graph.getNodeDict():
			print(node)
			parent_count = 0
			for edge in self.alg.graph.getEdges():
				if edge[1] == node:
					parent_count += 1
			if node == (0,0):
				self.assertEqual(parent_count, 0)
			else:
				self.assertEqual(parent_count, 1)

	def testAllNodesChildNumber(self):
		self.runAlgorithm()

		for node in self.alg.graph.getNodeDict():
			print(node)
			child_count = 0
			for edge in self.alg.graph.getEdges():
				if edge[0] == node:
					child_count += 1
			assert(child_count <= 4)

	def testGraphCoversEnvironment(self):
		self.runAlgorithm()

		for free_cell in self.alg.environment.getAllFreeCells():
			assert(free_cell in self.alg.graph.getNodeDict())


if __name__ == "__main__":
    unittest.main()  # run all tests