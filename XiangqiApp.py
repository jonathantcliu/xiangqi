import math
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.behaviors import DragBehavior
from kivy.uix.scatter import Scatter
from kivy.properties import ListProperty

Window.size = (800, 800)
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

def remove_out_of_bounds(position_list, x_min, x_max, y_min, y_max):
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
	pass

class Piece(DragBehavior, Image):
	def __init__(self, **args):
		self.size = (70, 70)
		self.id_number = 0
		self.is_active = False
		self.previous_position = (0, 0)
		self.valid_moves = []
		self.side = ''
		super(Piece, self).__init__(**args)
	
	def handle_invalid_move(self):
		print('handling invalid move')
		print('moving to previous position, which was ' + str(self.previous_position))
		self.pos = self.previous_position
	
	#def is_moving_onto_ally(self, corrected_x, corrected_y): #אולי השיטה הזאת מיושנת
		#positions = list(map(lambda p: [p.pos, p.source], self.parent.children))  #לקבל אחיי
		#matching = get_duplicate_piece((corrected_x, corrected_y), positions, 49) #לקבל כלים אשר נמצאים כאן
		#print('these match ' + str(matching))
		#print('i am ' + self.source)
		#if (len(matching) == 1): #רק אני בנקודה הזו. אין כלים אחרים
		#	return False
		
		#for index, match in enumerate(matching):
		#	if match[0] == self.pos and match[1] == self.source and index == 0: #זה אני! אל תעשה כלום
		#		continue
				
		#	if self.side == match[1].split('_', 1)[1].split('.', 1)[0]: #יש בעיה... מישהו באותו צבע כבר כאן
				#print('now i am ' + self.source)
		#		return True
				
		#return False #רק למקרה
	
	def get_unblocked_moves(self, move_list): #רשימת רשימות שבה תהיה רשימה אחת לכל כיוון
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
					
					#print('my side is ' + self.side + ' and match side is ' + match[1].split('_', 1)[1].split('.', 1)[0])
					if self.side == match[1].split('_', 1)[1].split('.', 1)[0]:
						print('move to ' + str(position) + ' would move onto ally')
						del direction[index:]
					else:
						print('move to ' + str(position) + ' would move onto enemy')
						del direction[(index + 1):]
						
			#print('direction now ' + str(direction))			
			result += direction
			
		return result
				

	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos):
			self.is_active = True
			self.previous_position = (int(self.x), int(self.y))
			print('position was ' + str(self.previous_position))
			#print('allowed moves are: ' + str(self.get_valid_moves()))
			self.valid_moves = self.get_valid_moves()
			print('allowed moves are: ' + str(self.valid_moves))
			
		return super(Piece, self).on_touch_down(touch)
		
	def on_touch_up(self, touch):		
		if self.collide_point(*touch.pos):
			if not self.is_active:
				print('i am an imposter and invalid move detected')
				#self.parent.active_piece_moving_onto = self.side
				#זיכרון בתמורה ליעילות. האם זה שווה את זה? 
				return True
				
			#if (self.parent.active_piece_moving_onto == self.side): #כאן אני מנסה למצוא בעיה אפשרית מוקדם ככל האפשר
				#self.handle_invalid_move()
			
			#else:			
			corrected_x = 46 + int(math.floor(self.x / 80.0)) * 80
			corrected_y = 40 + int(math.floor(self.y / 70.0)) * 70
			if (corrected_y > 320):
				corrected_y = int(corrected_y * 1.045)
			
			if corrected_x < 46:
				corrected_x = 46
			if corrected_x > 686:
				corrected_x = 686
			if corrected_y < 40:
				corrected_y = 40
			if corrected_y > 700:
				corrected_y = 700
			
			self.x = corrected_x
			self.y = corrected_y
					
			#print('i am moving to ' + str(corrected_x) + ',' + str(corrected_y))
			#if (self.is_valid_move):
			#to be implemented
			
			#if (not self.is_moving_onto_ally(corrected_x, corrected_y)): #and self.is_valid_move)
			if (corrected_x, corrected_y) in self.valid_moves:
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
			north_y = position[1] + 70 * (i + 1)
			south_y = position[1] - 70 * (i + 1)
			if north_y > 320:
				north_y = int(north_y * 1.045)
			if south_y > 320:
				south_y = int(south_y * 1.045)
				
			north.append((position[0], north_y))
			south.append((position[0], south_y))
		
		for i in range(8):
			east_x = position[0] + 80 * (i + 1)
			west_x = position[0] - 80 * (i + 1)
			east.append((east_x, position[1]))
			west.append((west_x, position[1]))
			
		return self.get_unblocked_moves([remove_out_of_bounds(north, 46, 686, 40, 700),
		remove_out_of_bounds(south, 46, 686, 40, 700),
		remove_out_of_bounds(east, 46, 686, 40, 700),
		remove_out_of_bounds(west, 46, 686, 40, 700)])

class Horse(Piece):
	def __init__(self, side):
		super(Horse, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/horse_' + side + '.png'
	
	def get_valid_moves(self, pos_x, pos_y):
		pass
	
class Elephant(Piece):
	def __init__(self, side):
		super(Elephant, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/elephant_' + side + '.png'
	
	def get_valid_moves(self, pos_x, pos_y):
		pass

class Minister(Piece):
	def __init__(self, side):
		super(Minister, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/minister_' + side + '.png'
	
	def get_valid_moves(self, pos_x, pos_y):
		pass

class General(Piece):
	def __init__(self, side):
		super(General, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/general_' + side + '.png'
	
	def get_valid_moves(self, pos_x, pos_y):
		pass

class Cannon(Piece):
	def __init__(self, side):
		super(Cannon, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/cannon_' + side + '.png'
	
	def get_valid_moves(self, pos_x, pos_y):
		pass

class Pawn(Piece):
	def __init__(self, side):
		super(Pawn, self).__init__()
		self.side = side
		self.source = './assets/' + side + '/pawn_' + side + '.png'
	
	def get_valid_moves(self, pos_x, pos_y):
		pass
	
		
	
class XiangqiApp(App):
	def build(self):
		root = Xiangqi()
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
					piece.pos = (46 + 80 * i, 40)
					piece.id_number = i + 1
				else:
					piece.pos = (46 + 80 * i, 700)
					piece.id_number = i + 17
				
				root.add_widget(piece)
			
			for i in range(2):
				piece = Cannon(sides[side_index])
				if side_index == 0:
					piece.pos = (126 + 6 * 80 * i, 180)
					piece.id_number = i + 10
				else:
					piece.pos = (126 + 6 * 80 * i, 550)
					piece.id_number = i + 26
				
				root.add_widget(piece)
			
			for i in range(5):
				piece = Pawn(sides[side_index])
				if side_index == 0:
					piece.pos = (46 + 160 * i, 250)
					piece.id_number = i + 12
				else:
					piece.pos = (46 + 160 * i, 480)
					piece.id_number = i + 28
					
				root.add_widget(piece)
			
			board_side = 1
			
		#root.turn = 'red'
		return root

XiangqiApp().run()
