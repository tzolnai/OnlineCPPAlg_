import os

def toTuple(tupleString):
	tupleString = tupleString.replace('(', '')
	tupleString = tupleString.replace(')', '')
	tupleString = tupleString.replace('[', '')
	tupleString = tupleString.replace(']', '')
	return tuple(int(x) for x in tupleString.split(','))

def readFile(path):
	inputFile = open(path, 'r')
	lines = inputFile.readlines()
	charging_station = toTuple(lines[0])
	energy_budget = int(lines[2])

	envLine = lines[1][1:-2].split(', ')
	env_width = int(envLine[0])
	env_height = int(envLine[1])

	obstacles = [toTuple(tup) for tup in envLine[3:]]

	return charging_station, energy_budget, env_width, env_height, obstacles
