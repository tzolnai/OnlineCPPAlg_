
import networkx as nx
import matplotlib.pyplot as plt
import math

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
		self.width = width
		self.height = height
		self.env_array = []
		for i in range(height):
			row = []
			for j in range(width):
				if (i,j) == charging_station:
					row.append(ENV_VALUE_STATION)					
				elif (i,j) in obstacle_list:
					row.append(ENV_VALUE_OBSTACLE)
				else:
					row.append(ENV_VALUE_EMPTY)
			self.env_array.append(row)

		# position of the charging station
		self.charging_station = charging_station
		
		# robot is at the charging station in the beginning
		self.robot_position = charging_station
		
		# contains all positions covered by obstacles
		self.obstacle_list = obstacle_list
	
	# for debugging
	def printOut(self):
		for i in range(self.height):
			for j in range(self.width):
				if self.robot_position == (i,j):
					print(ENV_VALUE_ROBOT, end =", ")
				else:
					print(self.env_array[i][j], end =", ")
			print("")

	def getFreeNeighbours(self, pos):
		assert_is_pos(pos)

		neighbours = []
		# west
		if (pos[1] < self.width - 1 and
		   self.env_array[pos[0]][pos[1] + 1] == ENV_VALUE_EMPTY):
			neighbours.append((pos[0], pos[1] + 1))
		# north
		if (pos[0] < self.height - 1 and
		   self.env_array[pos[0] + 1][pos[1]] == ENV_VALUE_EMPTY):
			neighbours.append((pos[0] + 1, pos[1]))
		# east
		if (pos[1] > 0 and
		   self.env_array[pos[0]][pos[1] - 1] == ENV_VALUE_EMPTY):
			neighbours.append((pos[0], pos[1] - 1))
		# south
		if (pos[0] > 0 and
		   self.env_array[pos[0] - 1][pos[1]] == ENV_VALUE_EMPTY):
			neighbours.append((pos[0] - 1, pos[1]))

		return neighbours;

class EnvGraph:
	def __init__(self, root, env):
		assert_is_pos(root)
		
		# dinamically build graph
		self.graph = nx.Graph(distance = 0, visited = False)		
		
		# it contains the root first (charging station)
		self.graph.add_node(root, distance = 0, visited = False)
		
		# store the unvisited nodes
		self.unvisited_nodes = []
		for neighbour in env.getFreeNeighbours(root):
			self.addNewNode({'pos': neighbour, 'distance': 1, 'visited': False}, root)
	
	# for debugging
	def printOut(self):
		# print the adjacency list
		for line in nx.generate_adjlist(self.graph):
			print(line)

		# write edgelist to grid.edgelist
		nx.write_edgelist(self.graph, path="grid.edgelist", delimiter=":")
		# read edgelist from grid.edgelist
		H = nx.read_edgelist(path="grid.edgelist", delimiter=":")

		nx.draw(H)
		plt.show()
	
	def addNewNode(self, node_dict, parent):
		assert_is_pos(parent)
		assert_is_pos(node_dict['pos'])
		assert(isinstance(node_dict['distance'], int))
		assert(isinstance(node_dict['visited'], bool))

		self.graph.add_node(node_dict['pos'], distance = node_dict['distance'], visited = node_dict['visited'])
		self.graph.add_edge(parent, node_dict['pos'])

		if node_dict['visited'] == False:
			self.unvisited_nodes.append({'pos': node_dict['pos'], 'distance': node_dict['distance']});

	def getShortestPath(self, source, target):
		assert_is_pos(source)
		assert_is_pos(target)

		return nx.shortest_path(self.graph, source=source, target=target)


class OnlineCPPAlg:
	def __init__(self):
		self.beta_constant = 3.0 / 4.0
		self.delta_sonstant = 1.0 / 10.0

		self.charging_station = (0,0)
		self.environment = Environment(4, 5, self.charging_station, [(1,1), (2,1), (1,2), (2,2)])
		self.environment.printOut()	
		
		self.robot_pos = (0,0)
		self.energy_budget = 20
		
		self.N_roots = [self.charging_station]
		
		self.graph = EnvGraph(self.charging_station, self.environment)
		#self.graph.printOut()


	def run(self):
		log_base = 1.0 / (1.0 - self.delta_sonstant)
		log_value = (self.energy_budget / 2.0) - 1.0
		for i in range(1, 2): #math.ceil(math.log(log_value, log_base)) + 1):
			Dcurr = math.floor(self.energy_budget - pow(1 - self.delta_sonstant, i - 1) * self.energy_budget)
			print('Dcurr')
			print(Dcurr)
			Dnext = math.floor(self.energy_budget - pow(1 - self.delta_sonstant, i) * self.energy_budget)
			print('Dnext')
			print(Dnext)
			Bcurr = self.energy_budget - Dcurr
			print('Bcurr')
			print(Bcurr)
			Bcurr_ = math.ceil((self.beta_constant + self.delta_sonstant) * Bcurr)
			print('Bcurr_')
			print(Bcurr_)
			Dcurr_ = self.energy_budget - Bcurr_
			print('Dcurr_')
			print(Dcurr_)
			
			#while self.find_unvisited_node_with_depth(0, Dcurr_):
			self.N_roots = self.cover(self.charging_station, i, Dcurr, Dcurr_, Dnext, self.N_roots)

	
	def cover(self, charging_station, i, Dcurr, Dcurr_, Dnext, N_roots):
		print('Dcurr')
		print(Dcurr)
		print('Dcurr_')
		print(Dcurr_)

		# check whether we have unvisited node with the right depth
		if not self.find_unvisited_node_with_depth(Dcurr, Dcurr_):
			return

		# find next node to visit
		node = self.find_closest_leftmost()
		print('node')
		print(node)

		# find Nroot node that we will use to go the the unvisited node
		(Nroot_node, Nroot_node_path) = self.find_closest_Nroot(node['pos'], N_roots)
		print('Nroot_node')
		print(Nroot_node)
		print('Nroot_node_path')
		print(Nroot_node_path)

		# go from charging stationg to Nroot first
		root_Nroot_path = self.graph.getShortestPath(self.charging_station, Nroot_node)
		print('root_Nroot_path')
		print(root_Nroot_path)
		self.go_on_path(root_Nroot_path)

		# go from Nroot to the unvisited node
		self.go_on_path(Nroot_node_path)

		# distance from charging stationg to the unvisited node
		node_distance = node['distance']
		print('node_distance')
		print(node_distance)

		budget_remain = self.energy_budget - node_distance
		print('budget_remain')
		print(budget_remain)
		
		# mark this node as visited
		self.graph.graph.nodes[node['pos']].update({'visited': True})
		self.robot_pos = node['pos']
		
		# visit all nodes we can visit with the current budget
		self.recursive_depth_first(node, budget_remain, Dcurr, Dcurr_)
		
		# we out of energy budget -> go back to the station.
		path_to_station = self.graph.getShortestPath(self.robot_pos, self.charging_station)
		self.go_on_path(path_to_station)

		return N_roots;

	def find_unvisited_node_with_depth(self, min_depth, max_depth):
		min_value = self.energy_budget
		for node in self.graph.unvisited_nodes:
			if node['distance'] >= min_depth and node['distance'] <= max_depth:
				return True

		return False

	def find_closest_leftmost(self):
		# find closest nodes
		min_value = self.energy_budget
		for node in self.graph.unvisited_nodes:
			if node['distance'] < min_value:
				min_value = node['distance']

		closest_nodes = []
		for node in self.graph.unvisited_nodes:
			if node['distance'] == min_value:
				closest_nodes.append(node);
		
		# TODO leftmost
		assert(len(closest_nodes) > 0)
		return closest_nodes[0];
	
	def find_closest_Nroot(self, node, Nroots):
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

	def go_on_path(self, path):
		print("go_on_path")
		print(path)
		if len(path) <= 1:
			return

		for node in range(1, len(path)):
			self.robot_pos = path[node]
			print(path[node])
			self.environment.robot_position = path[node]
			self.environment.printOut()
		
	def recursive_depth_first(self, node, budget, Dcurr, Dcurr_):
		for neighbour_pos in self.environment.getFreeNeighbours(node['pos']):		
			# add nodes as univisted
			neighbour_distance = node['distance'] + 1
			if neighbour_pos not in self.graph.graph.nodes:
				self.graph.addNewNode({'pos': neighbour_pos, 'distance': neighbour_distance, 'visited': False}, node['pos'])

			# we visit unvisited nodes here only.
			if neighbour_pos in self.graph.graph.nodes and self.graph.graph.nodes[neighbour_pos]['visited'] == True:
				print("visited already")
				print(self.graph.graph.nodes[neighbour_pos])
				print(neighbour_pos)
				continue

			# we can't visit this node because we won't be able go back to the charging station.
			if neighbour_distance > budget:
				print("too far")
				print(neighbour_distance)
				continue
			# we visit a contour here, so don't wonder too far.
			if neighbour_distance < Dcurr or neighbour_distance > Dcurr_:
				print("not on contour")
				print(neighbour_distance)
				continue
			
			# let visit this new node with the new budget
			print("visit a new node")
			print(neighbour_pos)
			
			self.graph.graph.nodes[neighbour_pos].update({'visited': True})
			self.robot_pos = neighbour_pos
			self.environment.robot_position = self.robot_pos
			self.environment.printOut()
			budget = budget - 1
			neighbour_dict = {'pos': neighbour_pos, 'distance': neighbour_distance}
			self.recursive_depth_first(neighbour_dict, budget, Dcurr, Dcurr_)
			

if __name__ == "__main__":
	alg = OnlineCPPAlg()
	alg.run()