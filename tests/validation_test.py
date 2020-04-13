import unittest
# Add the local path to the main script so we can import them.
import os, sys, inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
import OnlineCPPAlg as ocpp

config_files = [
	'tests/default_config.txt',
	'tests/empty_environment.txt',
	'tests/bigger_environment.txt',
	'tests/charging_station_different_pos.txt',
	'tests/bigger_budget.txt',
	'tests/env_1.txt',
	'tests/env_2.txt',
]

class graphValidationTest(unittest.TestCase):

	def testGraphValidation(self):
		for file in config_files:
			self.runGraphValidationOnConfig(file)

	def runGraphValidationOnConfig(self, file_name):
		print("Running validation test for: " + file_name)
		with open(file_name, "r") as file:
			line = file.readline()
			charging_station = eval(line)
			assert(isinstance(charging_station, tuple))
			assert(len(charging_station) == 2)

			line = file.readline()
			environment = eval(line)
			assert(isinstance(environment, tuple))
			assert(len(environment) == 4)

			line = file.readline()
			energy_budget = eval(line)
			assert(isinstance(energy_budget, int))

		self.runValidation(charging_station, environment, energy_budget)

	def runValidation(self, charging_station, environment, energy_budget):
		environment2 = ocpp.Environment(environment[0], environment[1], environment[2], environment[3])
		self.alg = ocpp.OnlineCPPAlg(charging_station, environment2, energy_budget)
		self.alg.run()

		self.checkAllNodesVisited()
		self.checkAllNodesPartOfTheTree()
		self.checkAllNodesHaveOneParent()
		self.checkAllNodesChildNumber()
		self.checkGraphCoversEnvironment()

	def checkAllNodesVisited(self):
		for node in self.alg.graph.getNodeDict():
			self.assertTrue(self.alg.graph.getNodeDict()[node]['visited'])

	def checkAllNodesPartOfTheTree(self):
		for node in self.alg.graph.getNodeDict():
			found = False
			for edge in self.alg.graph.getEdges():
				if edge[0] == node or edge[1] == node:
					found = True
					break
			self.assertTrue(found)

	def checkAllNodesHaveOneParent(self):
		for node in self.alg.graph.getNodeDict():
			parent_count = 0
			for edge in self.alg.graph.getEdges():
				if edge[1] == node:
					parent_count += 1
			if node == self.alg.charging_station:
				self.assertEqual(parent_count, 0)
			else:
				self.assertEqual(parent_count, 1)

	def checkAllNodesChildNumber(self):
		for node in self.alg.graph.getNodeDict():
			child_count = 0
			for edge in self.alg.graph.getEdges():
				if edge[0] == node:
					child_count += 1
			assert(child_count <= 4)

	def checkGraphCoversEnvironment(self):
		for free_cell in self.alg.environment.getAllFreeCells():
			assert(free_cell in self.alg.graph.getNodeDict())


if __name__ == "__main__":
    unittest.main()  # run all tests
