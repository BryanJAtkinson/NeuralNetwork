#input exec(open("./Drawing.py").read())

import matplotlib.pyplot
import numpy
import pygame
import random

class imageSave:
	def __init__(self, w, h):
		self.width = w
		self.height = h
		self.minX = w
		self.minY = h
		self.maxX = 0
		self.maxY = 0
		self.value = 0
		self.imageData = numpy.zeros(785) #replace with numpy.zeros(int(neuralNet.nodesPerLayer.split(",")[0]))
	
		pass
	
	def calculate(self, surface):
		imageDataIndex = 1
		
		#reposition maximum and minimum values to get a number in the center
		minXNew = max(int(self.minX - .3 * (self.maxX - self.minX)), 0)
		maxXNew = min(int(self.maxX + .15 * (self.maxX - self.minX)), self.width)
		minYNew = max(int(self.minY - .3 * (self.maxY - self.minY)), 0)
		maxYNew = min(int(self.maxY + .15 * (self.maxY - self.minY)), self.height)
		
		#Create a 28 by 28 pixel image
		for y in range(0, 28):
			for x in range (0, 28):
				for blockHeight in range(minYNew + int((maxYNew - minYNew) / 28 + 1) * y, min(minYNew + int((maxYNew - minYNew) / 28 + 1) * (y + 1), self.height)):
					for blockWidth in range(minXNew + int((maxXNew - minXNew) / 28 + 1) * x, min(minXNew + int((maxXNew - minXNew) / 28 + 1) * (x + 1), self.width)):
						color = surface.get_at((blockWidth,blockHeight))
						if color == (100, 100, 100, 255):
							self.imageData[imageDataIndex] = min(int(random.gauss(80, 25)), 255)
						elif color == (0, 0, 0, 255) and self.imageData[imageDataIndex] == 0:
							self.imageData[imageDataIndex] = min(int(random.gauss(220, 20)), 255) 
				
				imageDataIndex = imageDataIndex + 1	
		
		#Save the key number and save the 28 by 28 pixel image to the working directory
		self.imageData[0] = self.value
		plotting = self.imageData[1:]
		matplotlib.pyplot.imshow(plotting.reshape(28,28), cmap='Greys', interpolation='None')
		matplotlib.pyplot.savefig('figureDrawn.png')
		matplotlib.pyplot.close()
		
		pass
	
	def findExtremes(self, position1, position2):
		#calculate the minimum and maximum values
		if position1 > self.maxX:
			self.maxX = min(position1, self.width)
		if position1 < self.minX:
			self.minX = max(position1, 0)
		if position2 > self.maxY:
			self.maxY = min(position2, self.height)
		if position2 < self.minY:
			self.minY = max(position2, 0)
			
		pass
	
	def run(self):
		#start pygame
		pygame.init()

		#create the creen
		screen = pygame.display.set_mode((self.width, self.height))

		#How often to update the screen
		clock = pygame.time.Clock()

		black = (0, 0, 0)
		gray = (100,100, 100)
		white = (255, 255, 255)
		screen.fill(white)

		mouseClick = False
		running = True

		#Create a drawable texture and render with blit
		newSurface = pygame.Surface((self.width, self.height))
		newSurface.fill(white)
		screen.blit(newSurface, (0,0))

		#default mouse position and default image classifier
		position2 = (0, 0)
		value = 0

		while running:

			# Game	
			for event in pygame.event.get():
				#check for pressed keys
				pressed = pygame.key.get_pressed()
				if event.type == pygame.MOUSEBUTTONDOWN:
					position2 = pygame.mouse.get_pos()
					self.findExtremes(position2[0], position2[1])
					mouseClick = True
					
				elif event.type == pygame.MOUSEBUTTONUP:
					mouseClick = False
				
				#User inputs a value for the image key
				elif pressed[pygame.K_0]:
					self.value = 0
				elif pressed[pygame.K_9]:
					self.value = 9
				elif pressed[pygame.K_8]:
					self.value = 8
				elif pressed[pygame.K_7]:
					self.value = 7
				elif pressed[pygame.K_6]:
					self.value = 6
				elif pressed[pygame.K_5]:
					self.value = 5
				elif pressed[pygame.K_4]:
					self.value = 4
				elif pressed[pygame.K_3]:
					self.value = 3
				elif pressed[pygame.K_2]:
					self.value = 2
				elif pressed[pygame.K_1]:
					self.value = 1

				#Converts drawn image into a 28 by 28 pixel image and returns the array
				elif pressed[pygame.K_c]:
					self.imageData = numpy.zeros(785)
					self.calculate(newSurface)
				
				#resets the drawing space
				elif pressed[pygame.K_k]:
					newSurface.fill(white)
					screen.blit(newSurface, (0,0))
					self.imageData = numpy.zeros(785)
				
				#Controls the drawing of lines with the mouse
				if mouseClick == True:
					position = position2
					position2 = pygame.mouse.get_pos()
					
					self.findExtremes(position2[0], position2[1])
					
					oldX = position[0]
					oldY = position[1]
					newX = position2[0]
					newY = position2[1]
					
					pygame.draw.line(newSurface, black, (oldX, oldY), (newX, newY), 20)
					pygame.draw.line(newSurface, gray, (oldX + 10, oldY + 10), (newX + 10, newY + 10), 1)
					pygame.draw.line(newSurface, gray, (oldX - 10, oldY - 10), (newX - 10, newY - 10), 1)
					
					screen.blit(newSurface, (0,0))
				
				#Stop of loop in you press the 'X' button
				if event.type == pygame.QUIT:
					running = False

			#Display the drawn image as it is drawn
			pygame.display.flip()
			clock.tick(60)

		#Exit the drawing Window
		pygame.quit()
		
		#Return the 28 by 28 pixel image data
		return self.imageData

#width = 28 * 12
#height = 28 * 12
#calculate = imageSave(width, height)
#drawnImage = calculate.run()