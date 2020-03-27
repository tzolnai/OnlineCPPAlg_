
import networkx as nx
import matplotlib.pyplot as plt
import math
import copy

ENV_VALUE_EMPTY = "EMPTY"
ENV_VALUE_ROBOT = "ROBOT"
ENV_VALUE_STATION = "STATION"
ENV_VALUE_OBSTACLE = "OBSTACLE"

def assert_is_pos(pos):
	assert(isinstance(pos, tuple))
	assert(len(pos) == 2)
	assert(isinstance(pos[0], int))
	assert(isinstance(pos[1], int))

class Environment:
	def __init__(self, width, height, charging_station, obstacle_list):
		assert(isinstance(width, int))
		assert(isinstance(height, int))

		assert_is_pos(charging_station)

		assert(isinstance(obstacle_list, list))
		assert(charging_station not in obstacle_list)
	
		# a rectanlge area with the set width and height
		self.__width = width
		self.__height = height
		self.__env_array = []
		for i in range(height):
			row = []
			for j in range(width):
				if (i,j) == charging_station:
					row.append(ENV_VALUE_STATION)					
				elif (i,j) in obstacle_list:
					row.append(ENV_VALUE_OBSTACLE)
				else:
					row.append(ENV_VALUE_EMPTY)
			self.__env_array.append(row)

		# position of the charging station
		self.__charging_station = charging_station
		
		# contains all positions covered by obstacles
		self.__obstacle_list = obstacle_list
	
	# for debugging
	def printOut(self, robot_position):
		for i in range(self.__height):
			for j in range(self.__width):
				if robot_position == (i,j):
					print(ENV_VALUE_ROBOT, end =", ")
				else:
					print(self.__env_array[i][j], end =", ")
			print("")

	def getFreeNeighbours(self, pos):
		assert_is_pos(pos)

		neighbours = []
		# west
		if (pos[1] < self.__width - 1 and
		   self.__env_array[pos[0]][pos[1] + 1] == ENV_VALUE_EMPTY):
			neighbours.append((pos[0], pos[1] + 1))
		# north
		if (pos[0] < self.__height - 1 and
		   self.__env_array[pos[0] + 1][pos[1]] == ENV_VALUE_EMPTY):
			neighbours.append((pos[0] + 1, pos[1]))
		# east
		if (pos[1] > 0 and
		   self.__env_array[pos[0]][pos[1] - 1] == ENV_VALUE_EMPTY):
			neighbours.append((pos[0], pos[1] - 1))
		# south
		if (pos[0] > 0 and
		   self.__env_array[pos[0] - 1][pos[1]] == ENV_VALUE_EMPTY):
			neighbours.append((pos[0] - 1, pos[1]))

		return neighbours;

class EnvGraph:
	def __init__(self, root, env):
		assert_is_pos(root)

		# dinamically built graph
		self.__graph = nx.Graph(distance = 0, visited = False)

		# it contains the root first (charging station)
		self.__graph.add_node(root, distance = 0, visited = True)

		# store the unvisited nodes
		self.__unvisited_nodes = []
		for neighbour in env.getFreeNeighbours(root):
			self.addNewNode({'pos': neighbour, 'distance': 1, 'visited': False}, root)

	# for debugging
	def printOut(self):
		for node in self.__graph.nodes:
			print(node, end =": ")
			print(self.__graph.nodes[node])
	
	def addNewNode(self, node_dict, parent):
		assert_is_pos(parent)
		assert_is_pos(node_dict['pos'])
		assert(isinstance(node_dict['distance'], int))
		assert(isinstance(node_dict['visited'], bool))

		self.__graph.add_node(node_dict['pos'], distance = node_dict['distance'], visited = node_dict['visited'])
		self.__graph.add_edge(parent, node_dict['pos'])

		if node_dict['visited'] == False:
			self.__unvisited_nodes.append({'pos': node_dict['pos'], 'distance': node_dict['distance']});

	def markNodeAsVisited(self, node):
		assert_is_pos(node)

		self.__graph.nodes[node].update({'visited': True})
		for unvisited_node in self.__unvisited_nodes:
			if unvisited_node['pos'] == node:
				self.__unvisited_nodes.remove(unvisited_node);
				break

	def getUnivisitedNodes(self):
		return copy.deepcopy(self.__unvisited_nodes)

	def getShortestPath(self, source, target):
		assert_is_pos(source)
		assert_is_pos(target)

		return nx.shortest_path(self.__graph, source=source, target=target)

	def getNodeDict(self):
		return self.__graph.nodes

	def getParentOfNode(self, node):
		assert_is_pos(node)
		for edge in self.__graph.edges:
			assert_is_pos(edge[0])
			assert_is_pos(edge[1])
			if edge[1] == node:
				return edge[0]
		return None

	def getNodeWithDepth(self, depth):
		node_list = []
		for node in self.__graph.nodes:
			if self.__graph.nodes[node]['distance'] == depth:
				node_list.append(node);

		return node_list;


class OnlineCPPAlg:
	def __init__(self):
		self.beta_constant = 3.0 / 4.0
		self.delta_sonstant = 1.0 / 10.0

		self.charging_station = (0,0)
		self.environment = Environment(4, 5, self.charging_station, [(2,1), (3,1), (2,2), (3,2)])
		self.robot_pos = (0,0)

		self.energy_budget = 20
		
		self.N_roots = [self.charging_station]
		
		self.graph = EnvGraph(self.charging_station, self.environment)
		print("Initial state")
		self.printOut()

	def run(self):
		log_base = 1.0 / (1.0 - self.delta_sonstant)
		log_value = (self.energy_budget / 2.0) - 1.0
		for i in range(1, math.ceil(math.log(log_value, log_base)) + 1):
			Dcurr = math.floor(self.energy_budget - pow(1 - self.delta_sonstant, i - 1) * self.energy_budget)
			Dnext = math.floor(self.energy_budget - pow(1 - self.delta_sonstant, i) * self.energy_budget)
			Bcurr = self.energy_budget - Dcurr
			Bcurr_ = math.ceil((self.beta_constant + self.delta_sonstant) * Bcurr)
			Dcurr_ = self.energy_budget - Bcurr_
			
			while self.findUnvisitedNodeWithDepth(0, Dcurr_):
				self.cover(self.charging_station, i, Dcurr, Dcurr_, Dnext, self.N_roots)

			# update N list, to used as roots in the next round
			self.N_roots = self.graph.getNodeWithDepth(Dnext)

	
	def cover(self, charging_station, i, Dcurr, Dcurr_, Dnext, N_roots):

		# check whether we have unvisited node with the right depth
		if not self.findUnvisitedNodeWithDepth(Dcurr, Dcurr_):
			return

		# find next node to visit
		node = self.findClosestLeftmost()

		# find Nroot node that we will use to go the the unvisited node
		(Nroot_node, Nroot_node_path) = self.findClosestNroot(node['pos'], N_roots)

		# go from charging stationg to Nroot first
		root_Nroot_path = self.graph.getShortestPath(self.charging_station, Nroot_node)
		self.goOnPath(root_Nroot_path)

		# go from Nroot to the unvisited node
		self.goOnPath(Nroot_node_path)

		# distance from charging stationg to the unvisited node
		node_distance = node['distance']

		budget_remain = self.energy_budget - node_distance
		
		# visit all nodes we can visit with the current budget
		self.recursiveDepthFirst(node, budget_remain, Dcurr, Dcurr_)
		
		# we out of energy budget -> go back to the station.
		path_to_station = self.graph.getShortestPath(self.robot_pos, self.charging_station)
		self.goOnPath(path_to_station)

		return N_roots;

	def findUnvisitedNodeWithDepth(self, min_depth, max_depth):
		min_value = self.energy_budget
		for node in self.graph.getUnivisitedNodes():
			if node['distance'] >= min_depth and node['distance'] <= max_depth:
				return True

		return False

	def findClosestLeftmost(self):
		# find closest nodes
		min_value = self.energy_budget
		for node in self.graph.getUnivisitedNodes():
			if node['distance'] < min_value:
				min_value = node['distance']

		closest_nodes = []
		for node in self.graph.getUnivisitedNodes():
			if node['distance'] == min_value:
				closest_nodes.append(node);
		
		# we add items to the unvisited nodes list from left-to-right
		# so the first item is the leftmost.
		assert(len(closest_nodes) > 0)
		return closest_nodes[0];
	
	def findClosestNroot(self, node, Nroots):
		min_path_len = self.energy_budget
		min_path = []
		min_node = (-1, -1)
		for Nroot_node in Nroots:
			path = self.graph.getShortestPath(Nroot_node, node)
			if min_path_len > len(path):
				min_path_len = len(path)
				min_path = path
				min_node = Nroot_node
		
		assert(min_node != (-1, -1))
		return (min_node, min_path)

	def goOnPath(self, path):
		if len(path) <= 1:
			return

		for node in range(1, len(path)):
			self.doOneStep(path[node])

	def doOneStep(self, new_pos):
		assert_is_pos(new_pos)
		assert(self.robot_pos[0] == new_pos[0] or self.robot_pos[1] == new_pos[1])
		assert(abs(self.robot_pos[0] - new_pos[0]) == 1 or abs(self.robot_pos[1] - new_pos[1]) == 1)

		self.robot_pos = new_pos
		self.graph.markNodeAsVisited(new_pos)
		print("Robot did one step!")
		self.printOut()
		
	def recursiveDepthFirst(self, node, budget, Dcurr, Dcurr_):
		for neighbour_pos in self.environment.getFreeNeighbours(node['pos']):
			# we visit unexplored nodes only.
			if neighbour_pos in self.graph.getNodeDict():
				continue

			# add nodes as univisted
			neighbour_distance = node['distance'] + 1
			self.graph.addNewNode({'pos': neighbour_pos, 'distance': neighbour_distance, 'visited': False}, node['pos'])

			# we can't visit this node because we won't be able go back to the charging station.
			if neighbour_distance > budget:
				continue
			# we visit a contour here, so don't wonder too far.
			if neighbour_distance < Dcurr or neighbour_distance > Dcurr_:
				continue
			
			# let visit this new node with the new budget
			self.doOneStep(neighbour_pos)
			budget = budget - 1
			neighbour_dict = {'pos': neighbour_pos, 'distance': neighbour_distance}
			self.recursiveDepthFirst(neighbour_dict, budget, Dcurr, Dcurr_)

		# step back to parent
		parent = self.graph.getParentOfNode(node['pos'])
		self.doOneStep(parent)
		budget = budget - 1

	def printOut(self):
		self.environment.printOut(self.robot_pos)
		self.graph.printOut()


if __name__ == "__main__":
	alg = OnlineCPPAlg()
	alg.run()