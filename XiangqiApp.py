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
order = ['rook', 'horse', 'elephant', 'minister', 'general', 'minister', 'elephant', 'horse', 'rook']

def is_close_enough(points_a, points_b, margin):
	if points_a[0] - margin < points_b[0] and points_a[0] + margin > points_b[0]:
		if points_a[1] - margin < points_b[1] and points_a[1] + margin > points_b[1]:
			return True
	return False

def get_duplicate_piece(points, l, margin):
	matching = []
	for item in l:
		if is_close_enough(points, item[0], margin):
			
			matching.append(item)
			
	return matching

class Xiangqi(Widget):
	pass

class Piece(DragBehavior, Image):
	def __init__(self, **args):
		self.id_number = 0
		self.is_active = False
		self.previous_position = (0, 0)
		self.side = ''
		super(Piece, self).__init__(**args)
	
	def handle_invalid_move(self):
		print('handling invalid move')
		print('moving to previous position, which was ' + str(self.previous_position))
		self.pos = self.previous_position
	
	def is_moving_onto_ally(self, corrected_x, corrected_y):
		positions = list(map(lambda p: [p.pos, p.source], self.parent.children)) #לקבל אחיי
		matching = get_duplicate_piece((corrected_x, corrected_y), positions, 49) #לקבל כלים אשר נמצאים כאן
		print('these match ' + str(matching))
		print('i am ' + self.source)
		if (len(matching) == 1): #רק אני בנקודה הזו. אין כלים אחרים
			return False
		
		for index, match in enumerate(matching):
			if match[0] == self.pos and match[1] == self.source and index == 0: #זה אני! אל תעשה כלום
				continue
				
			if self.side == match[1].split('_', 1)[1].split('.', 1)[0]: #יש בעיה... מישהו באותו צבע כבר כאן
				#print('now i am ' + self.source)
				return True
				
		return False #רק למקרה
	
	#def is_valid_move(self):
		#return not is_moving_onto_ally
	#to be implemented in extended classes for each piece
	
	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos):
			self.is_active = True
			self.previous_position = (int(self.x), int(self.y))
			print('position was ' + str(self.previous_position))
			
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
					
			#print(corrected_x, corrected_y)
			#if (self.is_valid_move):
			#to be implemented
			
			if (not self.is_moving_onto_ally(corrected_x, corrected_y)): #and self.is_valid_move)
				self.x = corrected_x
				self.y = corrected_y
			else:
				self.handle_invalid_move()
			
		return super(Piece, self).on_touch_up(touch)
		
	
class XiangqiApp(App):
	def build(self):
		root = Xiangqi()
		other = 'black'
		if root.turn == 'black':
			other = 'red'
			
		for i in range(9):
			piece = Piece(pos = (46 + 80 * i, 40),
			source = './assets/' + root.turn + '/' + order[i] + '_' + root.turn + '.png', size = (70, 70))
			piece.side = root.turn
			piece.id_number = i + 1
			root.add_widget(piece)
		
		for i in range(2):
			piece = Piece(pos = (126 + 6 * 80 * i, 180),
			source = './assets/' + root.turn + '/cannon_' + root.turn + '.png', size = (70, 70))
			piece.side = root.turn
			piece.id_number = i + 10
			root.add_widget(piece)
		
		for i in range(5):
			piece = Piece(pos = (46 + 160 * i, 250),
			source = './assets/' + root.turn + '/pawn_' + root.turn + '.png', size = (70, 70))
			piece.side = root.turn
			piece.id_number = i + 12
			root.add_widget(piece)
			
		for i in range(9):
			piece = Piece(pos = (46 + 80 * i, 700),
			source = './assets/' + other + '/' + order[i] + '_' + other + '.png', size = (70, 70))
			piece.side = other
			piece.id_number = i + 17
			root.add_widget(piece)
			
		for i in range(2):
			piece = Piece(pos = (126 + 6 * 80 * i, 550),
			source = './assets/' + other + '/cannon_' + other + '.png', size = (70, 70))
			piece.side = other
			piece.id_number = i + 26
			root.add_widget(piece)
		
		for i in range(5):
			piece = Piece(pos = (46 + 160 * i, 480),
			source = './assets/' + other + '/pawn_' + other + '.png', size = (70, 70))
			piece.side = other
			piece.id_number = i + 28
			root.add_widget(piece)
		
		root.turn = 'red'
			
		return root

XiangqiApp().run()
