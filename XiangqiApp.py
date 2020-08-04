import math
from copy import deepcopy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import DragBehavior
from kivy.uix.scatter import Scatter
from kivy.properties import ListProperty

Window.size = (800, 800) #was (800, 800)
piece_size = Window.size[0] * 0.08
x_step = Window.size[0] * 0.1
y_step = Window.size[0] * 0.09
min_bounds = [Window.size[0] * 0.06, Window.size[0] * 0.05] #was [46, 40]
max_bounds = [min_bounds[0] + x_step * 8, min_bounds[1] + y_step * 9]
bounds = [min_bounds[0], max_bounds[0], min_bounds[1], max_bounds[1]]
#order = ['rook', 'horse', 'elephant', 'minister', 'general', 'minister', 'elephant', 'horse', 'rook']


def is_close_enough(points_a, points_b, margin):
	return points_a[0] - margin < points_b[0] and points_a[0] + margin > points_b[0] and \
	points_a[1] - margin < points_b[1] and points_a[1] + margin > points_b[1]

def get_duplicate_piece(points, l, margin):
	matching = []
	for item in l:
		if is_close_enough(points, item[0], margin):
			matching.append(item)
			
	return matching

def remove_out_of_bounds(position_list, bound_list):
	x_min = bound_list[0]
	x_max = bound_list[1]
	y_min = bound_list[2]
	y_max = bound_list[3]
	result = []
	count = 0
	for index, position in enumerate(position_list):
		if count > 3:
			return result
		if position[0] < x_min or position[0] > x_max or position[1] < y_min or position[1] > y_max:
			count += 1
		else:
			result.append(position)
				
	return result
			

class Xiangqi(Widget):
	def bring_to_front(self, widget):
		for child in self.children:
			if child == widget:
				self.remove_widget(widget)
				self.add_widget(widget)
				
	def send_to_back(self, widget):
		for child in self.children:
			if child == widget:
				self.remove_widget(widget)
				self.add_widget(widget, -1)
	#pass

class Piece(DragBehavior, Image):
	def __init__(self, **args):
		self.size = (piece_size, piece_size)
		self.id_number = 0
		self.is_active = False
		self.previous_position = (0, 0)
		self.valid_moves = []
		self.capture_moves = []
		self.side = ''
		super(Piece, self).__init__(**args)
	
	def handle_invalid_move(self):
		print('handling invalid move')
		print('moving to previous position, which was ' + str(self.previous_position))
		self.pos = self.previous_position
	
	def handle_capture(self, position):
		print('handling capture')
		for piece in self.parent.children:
			if (piece.pos[0], piece.pos[1]) == position and piece.side != self.side:
				print('removing captured piece at ' + str(position))
				self.parent.remove_widget(piece)
				return
	
	def get_unblocked_moves(self, move_list): #רשימת רשימות שבה תהיה רשימה אחת לכל כיוון
		cannon_screen_index = -1
		result = []
		positions = list(map(lambda p: [p.pos, p.source], self.parent.children))
		for direction in move_list:
			#print('direction was ' + str(direction))
			for index, position in enumerate(direction):
				matching = get_duplicate_piece(position, positions, 49)
				#print('matching is ' + str(matching))
				#if len(matching) == 1:
					#continue
				for match_index, match in enumerate(matching):
					if match[0] == self.pos and match[1] == self.source and match_index == 0: #אם יש מישהו כאני
						continue
					if 'red_dot' in match[1]:
						continue
					
					is_match_ally = (self.side == match[1].split('_', 1)[1].split('.', 1)[0])
					
					if 'cannon' not in self.source:
						#print('my side is ' + self.side + ' and match side is ' + match[1].split('_', 1)[1].split('.', 1)[0])
						if is_match_ally:
							print('move to ' + str(position) + ' would move onto ally')
							del direction[index:]
						else:
							print('move to ' + str(position) + ' would move onto enemy')
							del direction[(index + 1):]
							self.capture_moves.append(position)
					else:
						if cannon_screen_index == -1:
							cannon_screen_index = index
						else:
							if not is_match_ally:
								print('cannon can capture on ' + str(position))
								direction.append(position)
								self.capture_moves.append(position)
								#del direction[cannon_screen_index:]
								#del direction[(index + 1):]
							else:
								print('cannon blocked by ally on ' + str(position))
								#del direction[cannon_screen_index:]
								#del direction[index:]
								
							del direction[cannon_screen_index:]
							
			#print('direction now ' + str(direction))
			result += direction
			
		return result
				

	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos):
			self.parent.bring_to_front(self)
			self.is_active = True
			self.previous_position = (int(self.x), int(self.y))
			print('position was ' + str(self.previous_position))
			self.valid_moves = self.get_valid_moves()
			
			dot_layout = FloatLayout()
			for valid_move in self.valid_moves:
				dot_layout.add_widget(Image(source = './assets/red_dot.png', color = (255, 0, 0, 0.5),
				pos = (valid_move[0] + x_step * 0.35, valid_move[1] + 32), size_hint = (0.1, 0.1)))
			self.parent.add_widget(dot_layout, 1)

			print('allowed moves are: ' + str(self.valid_moves))
			
		return super(Piece, self).on_touch_down(touch)
		
	def on_touch_up(self, touch):
		if self.collide_point(*touch.pos):
			self.parent.send_to_back(self)
			for child in self.parent.children:
				if isinstance(child, FloatLayout):
					self.parent.remove_widget(child)

			if not self.is_active:
				print('i am an imposter and invalid move detected')
				#self.parent.active_piece_moving_onto = self.side
				#זיכרון בתמורה ליעילות. האם זה שווה את זה? 
				return True
				
			#if (self.parent.active_piece_moving_onto == self.side): #כאן אני מנסה למצוא בעיה אפשרית מוקדם ככל האפשר
				#self.handle_invalid_move()
			
			#else: bounds = [46, 686, 40, 694]
			corrected_x = int(bounds[0] + int(math.floor(self.x / x_step)) * x_step)
			corrected_y = int(bounds[2] + int(math.floor(self.y / y_step)) * y_step)
			#if (corrected_y > y_min_bound + y_step * 4):
				#corrected_y += river_offset
			
			if corrected_x < bounds[0]:
				corrected_x = bounds[0]
			if corrected_x > bounds[1]:
				corrected_x = bounds[1]
			if corrected_y < bounds[2]:
				corrected_y = bounds[2]
			if corrected_y > bounds[3]:
				corrected_y = bounds[3]
			
			self.x = corrected_x
			self.y = corrected_y
					
			print('i am moving to ' + str(corrected_x) + ',' + str(corrected_y))
			
			if (corrected_x, corrected_y) in self.valid_moves:
				if (corrected_x, corrected_y) in self.capture_moves:
					self.handle_capture((corrected_x, corrected_y))
				
				self.x = corrected_x
				self.y = corrected_y
				
			else:
				self.handle_invalid_move()
			
		return super(Piece, self).on_touch_up(touch)

class Rook(Piece):
	def __init__(self, side):
		super(Rook, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/rook_' + side + '.png'
	
	def get_valid_moves(self):
		position = self.pos
		north, south, east, west = [], [], [], []
		for i in range(9):
			north_y = int(position[1] + y_step * (i + 1))
			south_y = int(position[1] - y_step * (i + 1))
			
			north.append((position[0], north_y))
			south.append((position[0], south_y))
		
		for i in range(8):
			east_x = int(position[0] + 80 * (i + 1))
			west_x = int(position[0] - 80 * (i + 1))
			east.append((east_x, position[1]))
			west.append((west_x, position[1]))
			
		return self.get_unblocked_moves([remove_out_of_bounds(north, bounds),
		remove_out_of_bounds(south, bounds),
		remove_out_of_bounds(east, bounds),
		remove_out_of_bounds(west, bounds)])

class Horse(Piece):
	def __init__(self, side):
		super(Horse, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/horse_' + side + '.png'
	
	def get_valid_moves(self):
		return []
	
class Elephant(Piece):
	def __init__(self, side):
		super(Elephant, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/elephant_' + side + '.png'
	
	def get_valid_moves(self):
		return []

class Minister(Piece):
	def __init__(self, side):
		super(Minister, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/minister_' + side + '.png'
	
	def get_valid_moves(self):
		return []

class General(Piece):
	def __init__(self, side):
		super(General, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/general_' + side + '.png'
	
	def get_valid_moves(self):
		return []

class Cannon(Piece):
	def __init__(self, side):
		super(Cannon, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/cannon_' + side + '.png'
	
	def get_valid_moves(self):
		return []

class Pawn(Piece):
	def __init__(self, side):
		super(Pawn, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/pawn_' + side + '.png'
	
	def get_valid_moves(self):
		return []
	
	
class XiangqiApp(App):
	def build(self):
		root = Xiangqi()
		#piece_layout = FloatLayout()
		#root.add_widget(piece_layout)
		
		other = 'black'
		if root.host == 'black':
			other = 'red'
			
		sides = [root.host, other]
		
		for side_index in range(2): 
			for i in range(9):
				if i == 0 or i == 8:
					piece = Rook(sides[side_index])
				elif i == 1 or i == 7:
					piece = Horse(sides[side_index])
				elif i == 2 or i == 6:
					piece = Elephant(sides[side_index])
				elif i == 3 or i == 5:
					piece = Minister(sides[side_index])
				elif i == 4:
					piece = General(sides[side_index])
				if side_index == 0:
					piece.pos = (bounds[0] + x_step * i, bounds[2])
					piece.id_number = i + 1
				else:
					piece.pos = (bounds[0] + x_step * i, bounds[2] + y_step * 9)
					piece.id_number = i + 17
				
				root.add_widget(piece)
			
			for i in range(2):
				piece = Cannon(sides[side_index])
				if side_index == 0:
					piece.pos = (bounds[0] + x_step + 6 * x_step * i, bounds[2] + y_step * 2)
					#piece.pos = (126 + 6 * 80 * i, 180)
					piece.id_number = i + 10
				else:
					piece.pos = (bounds[0] + x_step + 6 * x_step * i, bounds[2] + y_step * 7) 
					#piece.pos = (126 + 6 * 80 * i, 550)
					piece.id_number = i + 26
				
				root.add_widget(piece)
			
			for i in range(5):
				piece = Pawn(sides[side_index])
				if side_index == 0:
					piece.pos = (bounds[0] + 2 * x_step * i, bounds[2] + y_step * 3)
					#piece.pos = (46 + 160 * i, 250)
					piece.id_number = i + 12
				else:
					piece.pos = (bounds[0] + 2 * x_step * i, bounds[2] + y_step * 6)
					#piece.pos = (46 + 160 * i, 480)
					piece.id_number = i + 28
					
				root.add_widget(piece)
			
			board_side = 1
			
		#root.turn = 'red'
		return root

XiangqiApp().run()
