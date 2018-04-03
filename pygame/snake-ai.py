import sys, pygame, time
from pygame import Rect
from random import randint

FIELD_SIZE = (width, height) = (60, 40)
COLOR_BLACK = (0,0,0)
COLOR_YELLOW = (255,255,0)
COLOR_GREEN = (0,255,0)
COLOR_BROWN = (150,75,0)
COLOR_WHITE = (255,255,255)
KEY_LEFT = 276
KEY_UP = 273
KEY_RIGHT = 275
KEY_DOWN = 274
SQUARE_SIDE = 10
FPS = 40
APPLE_COUNT = 10
START_BODY_SEGMENTS = 20
MAX_WAVE_PATHFIND_INDEX = (width**2+height**2)**0.5
POOP_ENABLED = False

class Field:
	def __init__(self):
		self.snake = Snake(30,5)
		self.apples = []
		self.poops = []
		self.target_apple = None
		for i in range(APPLE_COUNT):
		 	self.create_apple()

	def create_apple(self):
		self.apples.append(Apple(*self.get_free_point()))
		
	def add_poop(self, poop):
		self.poops.append(poop)
	
	def check_if_point_is_occupied_by_apples(self, point):
		for apple in self.apples:
			if apple.check_if_point_is_occupied(point): 
				return True
		return False
	
	def check_if_point_is_occupied_by_poops(self, point):
		if not(POOP_ENABLED):
			return False
		for poop in self.poops:
			if poop.check_if_point_is_occupied(point): 
				return True
		return False
		
	def check_if_point_is_free(self, point, ignoreApples = False):			
		occupied = self.snake.check_if_point_is_occupied(point)
		occupied |= point[0] < 0 or point[1] < 0 or point[0] >= width or point[1] >= height
		if not(ignoreApples):
			occupied |= self.check_if_point_is_occupied_by_apples(point)
		occupied |= self.check_if_point_is_occupied_by_poops(point)
		free = not(occupied)
		# print(str(point) + ": " + ("free" if free else "not free"))
		return free
		

	def get_free_point(self):
		free = False
		while not(free):
			point = (x, y) = randint(0, width), randint(0, height)
			free = self.check_if_point_is_free(point)
		return point
		
	@staticmethod
	def get_neighbour_points(point):
		# L-U-R-D
		left = (point[0]-1, point[1])
		up = (point[0], point[1]-1)
		right = (point[0]+1, point[1])
		down = (point[0], point[1]+1)
		res = []
		def point_is_valid(point):
			return point[0] >= 0 and point[0]<width and point[1] >= 0 and point[1] < height
			
		if point_is_valid(left): res.append(left)
		if point_is_valid(up): res.append(up)
		if point_is_valid(right): res.append(right)
		if point_is_valid(down): res.append(down)
		return res
		
	def get_wave_matrix(self):
		"""Creates a wave matrix for pathfinding"""
		BARRIER_MAP_KEY = -2
		matrix = {}
		# spread wave
		index = 0
		matrix[self.snake.head] = 0
		while (index <= MAX_WAVE_PATHFIND_INDEX):  # auto quit if apples are blocked
			# print("Index "+str(index)+":")
			# print(matrix)
			# time.sleep(1)
			if self.target_apple == None:
				for apple in self.apples:
					if apple.point in matrix: # if the wave has seen any apple - return matrix
						self.target_apple = apple
						return matrix
			elif self.target_apple.point in matrix:
				return matrix
			
			for point in list(matrix):
				if matrix[point] == index:
					neighbour_index = index+1
					for neighbour in Field.get_neighbour_points(point):
						if not(neighbour in matrix) and self.check_if_point_is_free(neighbour, ignoreApples=True):
							matrix[neighbour] = neighbour_index
			index += 1
			# visible_apples = matrix_keys_set.intersection(apple_points_set)
			# print("Index: " + str(index) + "; See " + str(len(visible_apples)) + " apples of " + str(len(self.apples)))
		for point in self.snake.body:
			matrix[point] = BARRIER_MAP_KEY
		for poop in self.poops:
			matrix[point] = BARRIER_MAP_KEY
		return matrix
	
	def get_direction(self, matrix):
		# build path
		if self.target_apple == None: # ALL apples are blocked! Panic! :D
			print("Panic!")
			available_points = Field.get_neighbour_points(self.snake.head)
			point_blocked_by_direction = (self.snake.head[0]-self.snake.speed[0], self.snake.head[1]-self.snake.speed[1])
			available_points.remove(point_blocked_by_direction)
			# available_points == 3 neighbours
			for point in available_points:
				if self.check_if_point_is_free(point, ignoreApples = True):	
					return (point[0]-self.snake.head[0], point[1]-self.snake.head[1])
			return (0,0) # todo: fill available space by body
		else:
			nearest_apple_point = self.target_apple.point
			current_point_value = matrix[nearest_apple_point]
			current_point = nearest_apple_point
			while current_point_value > 1:
				neighbours = Field.get_neighbour_points(current_point)
				# !!! print({p: matrix[p] for p in neighbours if p in matrix})
				available_points = [point for point in neighbours if (point in matrix and matrix[point] == current_point_value-1)]
				if len(available_points)==0:
					return (0,0)
				else:
					current_point = available_points[0]
					current_point_value = matrix[current_point]
			direction = (current_point[0]-self.snake.head[0],current_point[1]-self.snake.head[1])
			return direction
	
	def get_snake_direction(self):
		# wave algorithm
		matrix = self.get_wave_matrix()
		direction = self.get_direction(matrix)
		return direction

	def tick(self):
		direction = self.get_snake_direction()
		self.snake.turn(direction)
		self.snake.move()
		collided = self.snake.check_collisions()
		collided |= self.check_if_point_is_occupied_by_poops(self.snake.head)
		if not(collided):
			apples_to_eat = [apple for apple in self.apples if (apple.point[0], apple.point[1]) == (self.snake.head[0], self.snake.head[1])]
			if apples_to_eat:
				# eating
				apple = apples_to_eat[0]
				self.target_apple = None
				self.apples.remove(apple)
				self.create_apple()
				self.snake.grow()
		else: 
			
			global gameover
			gameover()
		
	def draw(self, screen):
		self.snake.draw(screen)
		for apple in self.apples:
			apple.draw(screen)
		for poop in self.poops:
			poop.draw(screen)
			

class Poop():
	def __init__(self, point):
		self.point = point
		
	def draw(self, screen):
		pygame.draw.rect(screen, COLOR_BROWN, pygame.Rect(self.point[0]*SQUARE_SIDE, self.point[1]*SQUARE_SIDE, SQUARE_SIDE, SQUARE_SIDE))
		
	def check_if_point_is_occupied(self, point):
		return point == self.point

class Apple():
	def __init__(self, x, y):
		self.point = (x,y)

	def draw(self, screen):
		pygame.draw.rect(screen, COLOR_GREEN, pygame.Rect(self.point[0]*SQUARE_SIDE, self.point[1]*SQUARE_SIDE, SQUARE_SIDE, SQUARE_SIDE))

	def check_if_point_is_occupied(self, point):
		return point == self.point
		
	def __str__(self):
		return str(self.point)
		
	def __repr__(self):
		return str(self.point)


class Snake():
	def __init__(self, startx, starty):
		self.head = (startx, starty)
		self.speed = (1,0)
		self.body = [(startx-(i+1),starty) for i in range(START_BODY_SEGMENTS)]
		self.need_to_poop = False
		
	def draw(self, screen):
		for segment in self.body:
			pygame.draw.rect(screen, COLOR_YELLOW, Rect(segment[0]*SQUARE_SIDE,segment[1]*SQUARE_SIDE,SQUARE_SIDE,SQUARE_SIDE))
		pygame.draw.rect(screen, COLOR_YELLOW, Rect(self.head[0]*SQUARE_SIDE,self.head[1]*SQUARE_SIDE,SQUARE_SIDE,SQUARE_SIDE))
		pygame.draw.rect(screen, COLOR_BLACK, Rect(self.head[0]*SQUARE_SIDE+SQUARE_SIDE/2,self.head[1]*SQUARE_SIDE+SQUARE_SIDE/2,SQUARE_SIDE/3,SQUARE_SIDE/3)) # eye
		
	def grow(self):
		self.body.insert(0, self.head)
		chance_to_poop = 20 # percent
		rnd = randint(0, 100+1)
		if rnd < chance_to_poop:
			self.need_to_poop = POOP_ENABLED
			
	def poop(self):
		global field
		field.add_poop(Poop(self.body[0]))
		# comment if snake needs to have diarrhea
		self.need_to_poop = False

	def move(self):
		if len(self.body) > 0 and self.head == self.body[0]:
			# grown at the previous move. body stays, nothing changes.
			self.head = (self.head[0] + self.speed[0], self.head[1] + self.speed[1])
		else:
			prev = self.head
			self.head = (self.head[0] + self.speed[0], self.head[1] + self.speed[1])
			# for segment in self.body:
			for i in range(len(self.body)):
				this = self.body[i]
				self.body[i] = prev
				prev = this
		if (self.need_to_poop):
			self.poop()

	def turn(self, direction):
		if self.speed == direction:
			return
		if direction == (0,0):
			return
		can_turn = not(direction[0] and self.speed[0] or direction[1] and self.speed[1])
		# magic but works :D
		if can_turn: 
			print("Turning to" + str(direction))
			self.speed = direction
	def check_collisions(self):
		collided = self.head in [el for el in self.body] or self.head[0] < 0 or self.head[1] < 0 or self.head[0] >= width or self.head[1] >= height
		return collided
	def check_if_point_is_occupied(self, point):
		return point in [el for el in self.body] or point == self.head


pygame.init()
pygame.display.set_caption('Smartsnake')
screen = pygame.display.set_mode((width*SQUARE_SIDE, height*SQUARE_SIDE))
field = Field()
stopped = False

def game_exit():
	pygame.quit()
	sys.exit()
	
def gameover():
	# global stopped
	# stopped = True
	global field
	pygame.font.init()
	myfont = pygame.font.SysFont('modenine', 20)
	score = len(field.snake.body) - START_BODY_SEGMENTS
	field.draw(screen) # draw last game frame on the final screen
	textsurface = myfont.render('SCORE: %d' % score, False, COLOR_WHITE)
	score_point = (SQUARE_SIDE, SQUARE_SIDE)
	text_size = (textwidth, textheight) = (textsurface.get_width(),textsurface.get_height())
	back_rect = Rect(score_point[0], score_point[1], textwidth, textheight)
	pygame.draw.rect(screen, COLOR_BLACK, back_rect)
	screen.blit(textsurface, score_point)
	pygame.display.flip()
	time.sleep(5)
	field = Field()
	# game_exit()

try:
	while not(stopped):
		for event in pygame.event.get():
			if event.type == pygame.QUIT: 
				game_exit()
		screen.fill(COLOR_BLACK)
		field.tick()
		field.draw(screen)
		pygame.display.flip()
		# time.sleep(1/FPS)
		# pygame.time.wait(int(1/FPS*1000))
finally:
	game_exit()
