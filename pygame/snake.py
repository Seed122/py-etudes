import sys, pygame, time
from pygame import Rect
from random import randint

SCREEN_SIZE = (width, height) = (400, 300)
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
FPS=60
MAX_FRAMES_BETWEEN_MOVES = 6
START_BODY_SEGMENTS = 20

class Field:
	def __init__(self):
		self.snake = Snake(300,50)
		self.apples = []
		self.poops = []
		for i in range(10):
			self.create_apple()

	def create_apple(self):
		self.apples.append(Apple(*self.get_free_cell()))
		
	def add_poop(self, poop):
		self.poops.append(poop)
	
	def check_if_cell_is_occupied_by_apples(self, cell):
		for apple in self.apples:
			if apple.check_if_cell_is_occupied(cell): 
				return True
		return False
	
	def check_if_cell_is_occupied_by_poops(self, cell):
		
		for poop in self.poops:
			if poop.check_if_cell_is_occupied(cell): 
				return True
		return False

	def get_free_cell(self):
		free = False
		while not(free):
			cell = (x, y) = randint(0, width/SQUARE_SIDE)*SQUARE_SIDE, randint(0, height/SQUARE_SIDE)*SQUARE_SIDE			
			occupied = self.snake.check_if_cell_is_occupied(cell)
			occupied |= self.check_if_cell_is_occupied_by_apples(cell)
			occupied |= self.check_if_cell_is_occupied_by_poops(cell)
			free = not(occupied)
		return cell

	def tick(self, force=False):
		moved = self.snake.move(force)
		if moved:
			collided = self.snake.check_collisions()
			collided |= self.check_if_cell_is_occupied_by_poops((self.snake.head.x, self.snake.head.y))
			if not(collided):
				apples_to_eat = [apple for apple in self.apples if (apple.rect.x, apple.rect.y) == (self.snake.head.x, self.snake.head.y)]
				if apples_to_eat:
					# eating
					apple = apples_to_eat[0]
					self.apples.remove(apple)
					self.create_apple()
					self.snake.grow()
					self.snake.accelerate()
			else: 
				global gameover
				gameover()
	
	def draw(self, screen):
		self.snake.draw(screen)
		for apple in self.apples:
			apple.draw(screen)
		for poop in self.poops:
			poop.draw(screen)
			
	def process_event(self, event):
		if event.type == pygame.KEYDOWN:
			if event.key == KEY_DOWN:
				self.snake.turn((0,1))
				self.tick(True)
			elif event.key == KEY_UP:
				self.snake.turn((0,-1))
				self.tick(True)
			elif event.key == KEY_RIGHT:
				self.snake.turn((1,0))
				self.tick(True)
			elif event.key == KEY_LEFT:
				self.snake.turn((-1,0))
				self.tick(True)

class Poop():
	def __init__(self, x, y):
		self.rect = pygame.Rect(x, y, SQUARE_SIDE, SQUARE_SIDE)
		
	def draw(self, screen):
		pygame.draw.rect(screen, COLOR_BROWN, self.rect)
		
	def check_if_cell_is_occupied(self, cell):
		return cell == (self.rect.x, self.rect.y)

class Apple():
	def __init__(self, x, y):
		self.rect = pygame.Rect(x, y, SQUARE_SIDE, SQUARE_SIDE)

	def draw(self, screen):
		pygame.draw.rect(screen, COLOR_GREEN, self.rect)

	def check_if_cell_is_occupied(self, cell):
		return cell == (self.rect.x, self.rect.y)


class Snake():
	def __init__(self, startx, starty):
		self.head = Rect(startx,starty,SQUARE_SIDE,SQUARE_SIDE)
		self.speed = (1,0)
		self.frames_between_moves = 15
		self.frames_after_last_move = 0
		self.body = [Rect(startx-(i+1)*SQUARE_SIDE,starty,SQUARE_SIDE,SQUARE_SIDE) for i in range(START_BODY_SEGMENTS)]
		self.need_to_poop = False
	def draw(self, screen):
		pygame.draw.rect(screen, COLOR_YELLOW, self.head)
		for segment in self.body:
			pygame.draw.rect(screen, COLOR_YELLOW, segment)
	def grow(self):
		self.body.insert(0, Rect(self.head.x, self.head.y, SQUARE_SIDE, SQUARE_SIDE))
		chance_to_poop = 20 # percent
		rnd = randint(0, 100+1)
		if rnd < chance_to_poop:
			self.need_to_poop = True

	def accelerate(self):
		if self.frames_between_moves > MAX_FRAMES_BETWEEN_MOVES:
			self.frames_between_moves -= 1
	def poop(self):
		global field
		field.add_poop(Poop(self.body[0].x, self.body[0].y))
		# закомментировать, если у змеи должна быть диарея
		# comment if snake needs to have diarrhea
		self.need_to_poop = False

	def move(self, force=False):
		if self.frames_after_last_move % self.frames_between_moves == 0 or force:
			if (self.head.x, self.head.y) == (self.body[0].x, self.body[0].y):
				# grown at the previous move
				self.head.x += self.speed[0]*SQUARE_SIDE
				self.head.y += self.speed[1]*SQUARE_SIDE
				
			else:
				prevx, prevy = self.head.x, self.head.y
				self.head.x += self.speed[0]*SQUARE_SIDE
				self.head.y += self.speed[1]*SQUARE_SIDE			
				for segment in self.body:
					thisx, thisy = segment.x, segment.y
					segment.x, segment.y = prevx, prevy
					prevx, prevy = thisx, thisy
			self.frames_after_last_move = 1
			res = True
		else:
			self.frames_after_last_move += 1
			res = False
		if (self.need_to_poop):
			self.poop()
		return res

	def turn(self, direction):
		can_turn = not(direction[0] and self.speed[0] or direction[1] and self.speed[1])
		# magic but works :D
		if can_turn: self.speed = direction
	def check_collisions(self):
		collided = (self.head.x,self.head.y) in [(el.x, el.y) for el in self.body] or self.head.x < 0 or self.head.y < 0 or self.head.x > (width-SQUARE_SIDE) or self.head.y > (height-SQUARE_SIDE)
		return collided
	def check_if_cell_is_occupied(self, cell):
		return cell in [(el.x, el.y) for el in self.body] or cell == (self.head.x, self.head.y)


pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
field = Field()
stopped = False

def game_exit():
	pygame.quit()
	sys.exit()
	
def gameover():
	global stopped
	stopped = True
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
	time.sleep(2)
	game_exit()

try:
	while not(stopped):
		for event in pygame.event.get():
			if event.type == pygame.QUIT: 
				game_exit()
			else: field.process_event(event)
		screen.fill(COLOR_BLACK)
		field.tick()
		field.draw(screen)
		pygame.display.flip()
		time.sleep(1/FPS)
finally:
	game_exit()
