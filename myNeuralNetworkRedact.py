###how to run
#cd to directory .py file is held in
#enter python3
#input import os
#input exec(open("./myNeuralNetwork.py").read())

import numpy
import matplotlib.pyplot
import scipy.special
import scipy.ndimage
import pymssql
import re
import Drawing

class neuralNetwork:
	#This is the constructor
	def __init__(self, numbLayers, numbNodesPerLayer, learningRate):
		self.numbLayers = numbLayers
		self.nodesPerLayer = numbNodesPerLayer
		self.weights = {}
		
		#Make Array of layer node sizes
		layerNumbList = self.nodesPerLayer.split(",")
		
		#Weights inside each dictionary value are W_ij. I is previous layer and J is next layer.
		for x in range(0, self.numbLayers - 1):
			self.weights["WeightLayer%s" % x] = numpy.random.normal(0.0, pow(int(layerNumbList[x]), -0.5),
									 (int(layerNumbList[x + 1]), int(layerNumbList[x])))
		
		#learning Rate
		self.learnR = learningRate
		
		#Activation and Inverse Activation Functions
		self.activate = lambda x: scipy.special.expit(x)
		self.inv_activate = lambda x: scipy.special.logit(x)
		
		pass

	def trainNN(self, inputs, targets):
		push = {}
		
		#Make Arrays 2D so they can be transposed
		push["values-1"] = numpy.array(inputs, ndmin = 2).T
		outVals = numpy.array(targets, ndmin = 2).T
		
		#Propegate inputs through the network		
		for x in range(0, self.numbLayers - 1):
			push["inputs%s" % x] = numpy.dot(self.weights["WeightLayer%s" % x], push["values%s" % (x - 1)])
			push["values%s" % x] = self.activate(push["inputs%s" % x])		
	
		#calculate basic errors
		push["errors%s" % (self.numbLayers - 1)] = (outVals - push["values%s" % (self.numbLayers - 2)])
		for x in reversed(range(1, self.numbLayers - 1)):
			push["errors%s" % x] = numpy.dot(self.weights["WeightLayer%s" % x].T, push["errors%s" % (x + 1)])
			
		#Update Weights
		for x in reversed(range(0, self.numbLayers - 1)):
			self.weights["WeightLayer%s" % x] += self.learnR * numpy.dot((push["errors%s" % (x + 1)] * push["values%s" % x] * (1.0 - push["values%s" % x])),
																		 numpy.transpose(push["values%s" % (x - 1)]))
		pass
		
	def testNN(self, inputs):
		pushed = {}
													
		#Make Arrays 2D so they can be transposed
		pushed["values-1"] = numpy.array(inputs, ndmin = 2).T
		
		#Propegate inputs through the network		
		for x in range(0, self.numbLayers - 1):
			pushed["inputs%s" % x] = numpy.dot(self.weights["WeightLayer%s" % x], pushed["values%s" % (x - 1)])
			pushed["values%s" % x] = self.activate(pushed["inputs%s" % x])
		
		#return and print the outputs
		print(pushed["values%s" % (self.numbLayers - 2)])
		return pushed["values%s" % (self.numbLayers - 2)]
		
	def reverseNetwork(self, outVals):
		dict = {}
		
		#Transpose Outvals into a vertical array
		dict["before_inv2"] = numpy.array(outVals, ndmin=2).T
		
		#invert the activation function and renormalize the results
		for x in reversed(range(0, self.numbLayers - 1)):
			dict["inVals%s" % x] = self.inv_activate(dict["before_inv%s" % (x + 1)])
			dict["before_inv%s" % x] = numpy.dot(self.weights["WeightLayer%s" % x].T, dict["inVals%s" % x])
			dict["before_inv%s" % x] -= numpy.min(dict["before_inv%s" % x])
			dict["before_inv%s" % x] /= numpy.max(dict["before_inv%s" % x])
			dict["before_inv%s" % x] *= 0.98
			dict["before_inv%s" % x] += 0.01
			
		return dict["before_inv0"]
	
def databaseConnect(columnName, tableName):
	#Connect to my database
	conn = pymssql.connect(server='<Redacted>.<Redacted>.com', port = 1433, user='<Redacted>', 
						   password='<Redacted>', database='<Redacted>')

	cursor = conn.cursor()

	cursor.execute("SELECT %s FROM %s" % (columnName, tableName))

	row = "Hello"
	dictionary = {}
	x = 0

	while (row != None):
		row = cursor.fetchone()
		dictionary["row%s" % x] = row
		x = x + 1

	conn.close()
	print("Success Reading Train")
	
	return dictionary

def training(nNetwork, inputArray, targetNodes, targetInt, epochs):
	#Standardize the inputs
	inputs = (numpy.asfarray(inputArray)/255.0*0.99) + 0.01
	
	#Rotate the inputs +/- 10 degress
	#inputsRotatePlus10 = scipy.ndimage.interpolation.rotate(inputs.reshape(28, 28), 10, cval=0.01, reshape = False).reshape(1,784)
	#inputsRotateMinus10 = scipy.ndimage.interpolation.rotate(inputs.reshape(28, 28), -10, cval=0.01, reshape = False).reshape(1, 784)
	
	#Standardize the targets
	targets = numpy.zeros(targetNodes) + 0.01
	targets[targetInt] = 0.99
	
	for x in range(0, epochs):
		nNetwork.trainNN(inputs, targets)
		#neuralNet.trainNN(inputsRotatePlus10, targets)
		#neuralNet.trainNN(inputsRotateMinus10, targets)

	pass

def testing(nNetwork, inputArray):
	inVals = (numpy.asfarray(inputArray) / 255.0 * 0.99) + 0.01
	outVal = nNetwork.testNN(inVals)

	result = numpy.argmax(outVal)
	print(result, "network's answer")
	
	return result



numbLayers = 3
numbNodesPerLayer = "784,100,10"
learningRate = 0.1
trainEpochs = 5;
													
neuralNet = neuralNetwork(numbLayers, numbNodesPerLayer, learningRate)
dictionary = databaseConnect("trainingdata", "mnist_train")

#Calculate the inputs and targets, then train the network
for x in range(0, len(dictionary) - 1):
	#Standardize the inputs
	total_record = re.split(',|\'', str(dictionary["row%s" % x]))
	
	training(neuralNet, total_record[2:-2], int(neuralNet.nodesPerLayer.split(",")[-1]), int(total_record[1]), trainEpochs)
	

#Record the Neural Network's Results
tracker = []
dictionaryTwo = databaseConnect("testingdata", "mnist_test")

#Go through all the records in the test data set
for x in range(0, len(dictionaryTwo) - 1):
	total_record = re.split(',|\'', str(dictionaryTwo["row%s" % x]))
	correct = int(total_record[1])
	result = testing(neuralNet, total_record[2:-2])
	print(correct, "correct label")
	#Append correct or incorrect to list
	if (result == correct):
		tracker.append(1)
	else:
		tracker.append(0)
	pass
	
print(tracker)
score_array = numpy.asarray(tracker)
print("Performance = ", score_array.sum() / score_array.size)


#Backquery the network to see what the network thinks a number is
for x in range(0, 10):
	#create the input for reverseNetwork
	outVal = numpy.zeros(int(neuralNet.nodesPerLayer.split(",")[-1])) + 0.01
	outVal[x] = 0.99
	print(outVal)
	
	#Get Image Data
	reverseImage = neuralNet.reverseNetwork(outVal)
	matplotlib.pyplot.imshow(reverseImage.reshape(28,28), cmap='Greys', interpolation='None')
	matplotlib.pyplot.savefig('figure%s.png' % x)

	
#Draw an image and train the network
customTrain = True
while customTrain:
	width = 28 * 12
	height = 28 * 12
	calculate = Drawing.imageSave(width, height)
	drawnImage = calculate.run()
	
	training(neuralNet, drawnImage[1:], int(neuralNet.nodesPerLayer.split(",")[-1]), int(drawnImage[0]), trainEpochs)
	
	verifyContinue = input("Train another number? ")
	if (verifyContinue == "no" or verifyContinue == "No"):
		customTrain = False
		

#Draw an Image and test the network	
customTest = True
while customTest:
	width = 28 * 12
	height = 28 * 12
	calculate = Drawing.imageSave(width, height)
	drawnImage = calculate.run()
	correct = int(drawnImage[0])
	result = testing(neuralNet, drawnImage[1:])
	print(correct, "correct label")
	
	verifyContinue = input("Test another number? ")
	if (verifyContinue == "no" or verifyContinue == "No"):
		customTest = False
