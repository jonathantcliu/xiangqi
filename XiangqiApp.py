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
	#count = 0
	for index, position in enumerate(position_list):
		if not (position[0] < x_min or position[0] > x_max or position[1] < y_min or position[1] > y_max):
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
	
	def find_piece(self, position):
		for piece in self.children:
			if (piece.pos[0], piece.pos[1]) == position:
				return piece
		return None
		

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
				self.capture_moves = []
	
	def is_check_after_move(self, position):
		danger = False
		is_occupied = self.parent.find_piece(position)
		if is_occupied:
			print('next move is capture')
			self.parent.remove_widget(is_occupied)
		
		self.pos = position
		enemy_pieces = [piece for piece in self.parent.children if piece.side != self.side]
		general = [piece for piece in self.parent.children if 'general' in piece.source and piece.side == self.side][0]
		general_pos = (general.pos[0], general.pos[1])
		
		for enemy in enemy_pieces:
			old_capture = enemy.capture_moves
			old_valid = enemy.valid_moves
			enemy.valid_moves = enemy.get_valid_moves()
			if general_pos in enemy.valid_moves:
				print('check')
				danger = True
			enemy.capture_moves = old_capture
			enemy.valid_moves = old_valid
		
		self.pos = self.previous_position
		if is_occupied:
			self.parent.add_widget(is_occupied, -1)
		return danger
			
	def get_unblocked_moves(self, move_list, passed_by_direction = True): #רשימת רשימות שבה תהיה רשימה אחת לכל כיוון
		cannon_screen_index = -1
		cannon_capture_found = False
		result = []
		positions = list(map(lambda p: [p.pos, p.source], self.parent.children))
		for direction in move_list:
			for index, position in enumerate(direction):
				matching = get_duplicate_piece(position, positions, 49)
				for match_index, match in enumerate(matching):
					is_match_ally = (self.side == match[1].split('_', 1)[1].split('.', 1)[0])
					if cannon_screen_index == -1:
						if is_match_ally:
							if passed_by_direction:
								del direction[index:]
							else:
								direction = list(filter(lambda pos: pos != position, direction))
						else:
							if 'cannon' not in self.source:
								if passed_by_direction:
									del direction[(index + 1):]
								else:
									print('can capture at position ' + str(position))
									
								if position not in self.capture_moves:
									self.capture_moves.append(position)
							else:
								cannon_screen_index = index
								if position == direction[-1]: #screen to nowhere!
									del direction[cannon_screen_index:]
								
								#cannon_screen_position = position
							
					elif 'cannon' in self.source:
						if not is_match_ally:
							cannon_capture_found = True
							result.append(position)
							if position not in self.capture_moves:
								self.capture_moves.append(position)
						else:
							pass
							#print('cannon blocked by ally on ' + str(position))

						del direction[cannon_screen_index:]
			
			if cannon_screen_index != -1 and not cannon_capture_found:
				del direction[cannon_screen_index:]
				
			cannon_screen_index = -1
			result += direction
			
		return result

	def on_touch_down(self, touch):
		if self.parent.turn != self.side and self.collide_point(*touch.pos):
			return False
		if self.collide_point(*touch.pos):
			self.parent.bring_to_front(self)
			self.is_active = True
			self.previous_position = (int(self.x), int(self.y))
			#if 'general' not in self.source:
			self.capture_moves = []
			move_list = self.get_valid_moves()
			self.valid_moves = [move for move in move_list if not self.is_check_after_move(move)]
			#self.valid_moves = self.get_valid_moves()
			
			dot_layout = FloatLayout()
			for valid_move in self.valid_moves:
				dot_x = valid_move[0] + x_step * 0.34
				dot_y = valid_move[1] + y_step * 0.395
				if valid_move[1] > bounds[2] + y_step * 4:
					dot_y += 5
				
				if valid_move in self.capture_moves:
					dot_layout.add_widget(Image(source = './assets/red_dot.png', color = (255, 0, 0, 1),
					pos = (dot_x, dot_y), size_hint = (0.1, 0.1)))
				else:
					dot_layout.add_widget(Image(source = './assets/red_dot.png', color = (255, 0, 0, 0.5),
					pos = (dot_x, dot_y), size_hint = (0.1, 0.1)))
					
					
			self.parent.add_widget(dot_layout, 1)

			print('allowed moves are: ' + str(self.valid_moves))
			print('capture moves are: ' + str(self.capture_moves))
			
		return super(Piece, self).on_touch_down(touch)
		
	def on_touch_up(self, touch):
		if self.parent.turn != self.side:
			print('not your turn!')
			return False
		if self.collide_point(*touch.pos):
				
			self.parent.send_to_back(self)
			for child in self.parent.children:
				if isinstance(child, FloatLayout):
					self.parent.remove_widget(child)

			if not self.is_active:
				return True

			corrected_x = int(bounds[0] + int(math.floor(self.x / x_step)) * x_step)
			corrected_y = int(bounds[2] + int(math.floor(self.y / y_step)) * y_step)
			
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
			
			if (corrected_x, corrected_y) in self.valid_moves:
				if (corrected_x, corrected_y) in self.capture_moves:
					self.handle_capture((corrected_x, corrected_y))
				
				self.x = corrected_x
				self.y = corrected_y
				if self.parent.turn == 'red':
					self.parent.turn = 'black'
				else:
					self.parent.turn = 'red'
				
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
			east_x = int(position[0] + x_step * (i + 1))
			west_x = int(position[0] - x_step * (i + 1))
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
		position = self.pos
		moves = []
		horse_legs = [(position[0] + x_step, position[1]),
		(position[0] - x_step, position[1]),
		(position[0], position[1] - y_step),
		(position[0], position[1] + y_step)]
		for piece in self.parent.children:
			if (piece.pos[0], piece.pos[1]) in horse_legs:
				index = horse_legs.index((piece.pos[0], piece.pos[1]))
				horse_legs[index] = (0, 0)
		
		for index, leg in enumerate(horse_legs):
			#print('checking leg ' + str(leg))
			if index < 2 and leg != (0, 0):
				moves.append((leg[0], leg[1] + y_step))
				moves.append((leg[0], leg[1] - y_step))
			elif index > 1 and leg != (0, 0):
				moves.append((leg[0] - x_step, leg[1]))
				moves.append((leg[0] + x_step, leg[1]))
		
		#print(moves)
		return self.get_unblocked_moves([remove_out_of_bounds(moves, bounds)], passed_by_direction = False)
		#return []
	
class Elephant(Piece):
	def __init__(self, side):
		super(Elephant, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/elephant_' + side + '.png'
	
	def get_valid_moves(self):
		position = self.pos
		northeast, southeast, southwest, northwest = [], [], [], []
		northeast_offset = (x_step * 2, y_step * 2)
		southeast_offset = (x_step * 2, y_step * -2)
		southwest_offset = (x_step * -2, y_step * -2)
		northwest_offset = (x_step * -2, y_step * 2)
		for i in range(4):
			if i == 0:
				northeast.append((position[0] + northeast_offset[0], position[1] + northeast_offset[1]))
			elif i == 1:
				southeast.append((position[0] + southeast_offset[0], position[1] + southeast_offset[1]))
			if i == 2:
				southwest.append((position[0] + southwest_offset[0], position[1] + southwest_offset[1]))
			if i == 3:
				northwest.append((position[0] + northwest_offset[0], position[1] + northwest_offset[1]))
		
		self_is_host = self.side == self.parent.host
		if self_is_host:
			elephant_bounds = [min_bounds[0], max_bounds[0], min_bounds[1], min_bounds[1] + y_step * 4]
		else:
			elephant_bounds = [min_bounds[0], max_bounds[0], min_bounds[1] + y_step * 5, max_bounds[1]]
		
		return self.get_unblocked_moves([remove_out_of_bounds(northeast, elephant_bounds),
		remove_out_of_bounds(southeast, elephant_bounds),
		remove_out_of_bounds(southwest, elephant_bounds),
		remove_out_of_bounds(northwest, elephant_bounds)])

class Minister(Piece):
	def __init__(self, side):
		super(Minister, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/minister_' + side + '.png'
	
	def get_valid_moves(self):
		position = self.pos
		northeast, southeast, southwest, northwest = [], [], [], []
		northeast_offset = (x_step, y_step)
		southeast_offset = (x_step, -y_step)
		southwest_offset = (-x_step, -y_step)
		northwest_offset = (-x_step, y_step)
		
		for i in range(4):
			if i == 0:
				northeast.append((position[0] + northeast_offset[0], position[1] + northeast_offset[1]))
			elif i == 1:
				southeast.append((position[0] + southeast_offset[0], position[1] + southeast_offset[1]))
			if i == 2:
				southwest.append((position[0] + southwest_offset[0], position[1] + southwest_offset[1]))
			if i == 3:
				northwest.append((position[0] + northwest_offset[0], position[1] + northwest_offset[1]))
		
		self_is_host = self.side == self.parent.host
		if self_is_host:
			minister_bounds = [min_bounds[0] + x_step * 3, min_bounds[0] + x_step * 5, min_bounds[1], min_bounds[1] + y_step * 2]
		else:
			minister_bounds = [min_bounds[0] + x_step * 3, min_bounds[0] + x_step * 5, max_bounds[1] - y_step * 2, max_bounds[1]]
		
		return self.get_unblocked_moves([remove_out_of_bounds(northeast, minister_bounds),
		remove_out_of_bounds(southeast, minister_bounds),
		remove_out_of_bounds(southwest, minister_bounds),
		remove_out_of_bounds(northwest, minister_bounds)])

class General(Piece):
	def __init__(self, side):
		super(General, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/general_' + side + '.png'
	
	def get_valid_moves(self):
		position = self.pos
		north, south, east, west = [], [], [], []
		north_offset = (0, y_step)
		south_offset = (0, -y_step)
		east_offset = (x_step, 0)
		west_offset = (-x_step, 0)
		
		for i in range(4):
			if i == 0:
				north.append((position[0] + north_offset[0], position[1] + north_offset[1]))
			elif i == 1:
				south.append((position[0] + south_offset[0], position[1] + south_offset[1]))
			if i == 2:
				east.append((position[0] + east_offset[0], position[1] + east_offset[1]))
			if i == 3:
				west.append((position[0] + west_offset[0], position[1] + west_offset[1]))
		
		#perform 飛將 check
		general_pos = []
		same_file = [piece for piece in self.parent.children if (self.pos[0] == piece.pos[0])]
		if same_file:
			same_file.sort(key = lambda p: p.pos[1])
			#print('same file has ' + str(same_file))
		
		for x, y in zip(same_file, same_file[1:]):
			if 'general' in x.source and 'general' in y.source:
				print('no screen')
				if x == self:
					self.capture_moves.append((y.pos[0], y.pos[1]))
					general_pos.append((y.pos[0], y.pos[1]))
				else:
					self.capture_moves.append((x.pos[0], x.pos[1]))
					general_pos.append((x.pos[0], x.pos[1]))
					
		
		self_is_host = self.side == self.parent.host
		if self_is_host:
			general_bounds = [min_bounds[0] + x_step * 3, min_bounds[0] + x_step * 5, min_bounds[1], min_bounds[1] + y_step * 2]
		else:
			general_bounds = [min_bounds[0] + x_step * 3, min_bounds[0] + x_step * 5, max_bounds[1] - y_step * 2, max_bounds[1]]
			
		return self.get_unblocked_moves([remove_out_of_bounds(north, general_bounds),
		remove_out_of_bounds(south, general_bounds),
		remove_out_of_bounds(east, general_bounds),
		remove_out_of_bounds(west, general_bounds)]) + general_pos

class Cannon(Piece):
	def __init__(self, side):
		super(Cannon, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/cannon_' + side + '.png'
	
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

class Pawn(Piece):
	def __init__(self, side):
		super(Pawn, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/pawn_' + side + '.png'
	
	def get_valid_moves(self):
		result = []
		if self.side == self.parent.host:
			result.append((self.pos[0], self.pos[1] + y_step))
		else:
			result.append((self.pos[0], self.pos[1] - y_step))
		
		self_is_host = self.side == self.parent.host
		if self.pos[1] > bounds[2] + y_step * 4 and self_is_host or \
		self.pos[1] < bounds[3] - y_step * 4 and not self_is_host:
				result.append((self.pos[0] - x_step, self.pos[1]))
				result.append((self.pos[0] + x_step, self.pos[1]))
		
		return self.get_unblocked_moves([remove_out_of_bounds(result, bounds)], passed_by_direction = False)
	
	
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
