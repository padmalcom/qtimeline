import numpy

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QPoint, QLine, QRect, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QBrush, QPalette, QPen, QPolygon, QPainterPath
from PyQt6.QtWidgets import QWidget
from operator import attrgetter

__textColor__ = QColor(187, 187, 187)
__backgroudColor__ = QColor(60, 63, 65)
__font__ = QFont('Decorative', 7)

class Sample:

	def __init__(self, duration, color=Qt.GlobalColor.darkYellow, picture=None, audio=None, text="", track=0):
		self.duration = duration
		self.color = color 
		self.defColor = color
		self.track = track
		self.text = text
		if picture is not None:
			self.picture = picture.scaledToHeight(45)
		else:
			self.picture = None
		self.startPos = 0
		self.endPos = self.duration


class QTimeLine(QWidget):

	positionChanged = pyqtSignal(int)
	selectionChanged = pyqtSignal(Sample)

	def __init__(self, duration, length, track_names = ["track1"], track_height=20, *args, **kwargs):
		super(QWidget, self).__init__(*args, **kwargs)
		self.duration = duration
		self.length = length
		self.track_height = track_height
		
		self.setSizePolicy(
			QtWidgets.QSizePolicy.Policy.MinimumExpanding,
			QtWidgets.QSizePolicy.Policy.MinimumExpanding
		)
		
		self.LEFT_PADDING = 40
		self.RIGHT_PADDING = 10
		
		default_palette = self.palette()
		self.text_color = default_palette.windowText().color()
		self.backgroud_color = default_palette.text().color()
		self.horizontal_line_color = Qt.GlobalColor.red

		self.backgroundColor = __backgroudColor__
		self.textColor = __textColor__
		self.font = __font__
		self.pos = None
		self.pointerPos = None
		self.pointerTimePos = None
		self.selectedSample = None
		self.clicking = False  # Check if mouse left button is being pressed
		self.is_in = False  # Check if mouse is in the widget
		self.samples = []  # List of samples
		self.track_names = track_names

		self.setMouseTracking(True)
		self.setAutoFillBackground(True)

		self.initUI()

	def initUI(self):
		self.setGeometry(300, 300, self.length, 200)
		#self.setWindowTitle("TESTE")

		# Set Background
		pal = QPalette()
		#pal.setColor(QPalette.ColorRole.Window, self.backgroundColor) #QPalette.Background
		self.setPalette(pal)

	def paintEvent(self, event):
		qp = QPainter()
		qp.begin(self)
		qp.setPen(self.textColor)
		qp.setFont(self.font)
		qp.setRenderHint(QPainter.RenderHint.Antialiasing)	
		scale = self.getScale()
			
		# Draw horizontal line
		qp.setPen(QPen(Qt.GlobalColor.darkCyan, 5, Qt.PenStyle.SolidLine))
		qp.drawLine(0, 40, self.width() - self.RIGHT_PADDING, 40)

		# Draw horizontal track lines
		qp.setPen(QPen(self.textColor))
		max_track = max(self.samples, key=attrgetter('track'))
		for i in range(1, 3 + max_track.track):
			track_text = self.track_names[i-1] if len(self.track_names) > i-1 else ""
			qp.drawText(0, self.track_height*(i+1), self.LEFT_PADDING, self.track_height, Qt.AlignmentFlag.AlignVCenter, track_text)
			qp.drawLine(0, self.track_height*(i+1), self.width() - self.RIGHT_PADDING, self.track_height*(i+1))
		
		# draw vertical time splitters
		for index, pos_x in enumerate(range(self.LEFT_PADDING, self.width() - self.RIGHT_PADDING, 30)):
			if index % 3 == 0:
				# Draw time text
				qp.drawText(pos_x-50, 0, 100, 100, Qt.AlignmentFlag.AlignHCenter, self.get_time_string((pos_x  - self.LEFT_PADDING) * scale))
				qp.drawLine(pos_x, 20, pos_x, 40)
			else:
				qp.drawLine(pos_x, 30, pos_x, 30)
		

		# draw moving, horizontal line
		qp.setPen(QPen(self.horizontal_line_color))
		if self.pos is not None and self.is_in:
			if (self.pos.x() >= 0 and self.pos.x() <= self.width() - self.LEFT_PADDING - self.RIGHT_PADDING):
				#qp.drawLine(self.pos.x() + self.PADDING, 0, self.pos.x() + self.PADDING, 40)
				pass
				
		# calculate pos of marker
		if self.pointerPos is not None and self.pointerPos >= 0:
			if self.pointerPos <= self.width() - self.LEFT_PADDING - self.RIGHT_PADDING:
				line = QLine(QPoint(self.pointerTimePos/self.getScale() + self.LEFT_PADDING, 40),
							 QPoint(self.pointerTimePos/self.getScale() + self.LEFT_PADDING, self.height()))
				poly = QPolygon([QPoint(self.pointerTimePos/self.getScale() - 5 + self.LEFT_PADDING, 20),
								 QPoint(self.pointerTimePos/self.getScale() + 5 + self.LEFT_PADDING, 20),
								 QPoint(self.pointerTimePos/self.getScale() + self.LEFT_PADDING, 40)])
			else:
				line = QLine(QPoint(self.width()-self.RIGHT_PADDING, 40), QPoint(self.width()-self.RIGHT_PADDING, self.height()))
				poly = QPolygon([QPoint(-5 + self.width()-self.RIGHT_PADDING, 20), QPoint(5 + self.width()-self.RIGHT_PADDING, 20), QPoint(self.width()-self.RIGHT_PADDING, 40)])
		else:
			line = QLine(QPoint(self.LEFT_PADDING, 40), QPoint(self.LEFT_PADDING, self.height()))
			poly = QPolygon([QPoint(-5 + self.LEFT_PADDING, 20), QPoint(5 + self.LEFT_PADDING, 20), QPoint(self.LEFT_PADDING, 40)])

		qp.setPen(QPen(Qt.GlobalColor.darkCyan))
				
		# Draw samples
		t = 0 + self.LEFT_PADDING*scale
		for sample in self.samples:
						
			# Clear clip path
			#path = QPainterPath()
			#path.addRoundedRect(QRectF(t / scale, 40 + self.track_height*sample.track, sample.duration / scale, 200), 10, 10)
			#qp.setClipPath(path)
			
		
			# Draw sample
			path = QPainterPath()
			qp.setPen(sample.color)
			path.addRoundedRect(
				QRectF(
					t/scale,
					40 + self.track_height*sample.track,
					sample.duration/scale,
					self.track_height
				), 10, 10)
			sample.startPos = t/scale
			sample.endPos = t/scale + sample.duration/scale
			qp.fillPath(path, sample.color)				
			qp.drawPath(path)
			
			# draw texts
			if sample.text:
				qp.setPen(QPen(Qt.GlobalColor.black))
				qp.drawText(t / scale, 45 + self.track_height*sample.track, sample.duration / scale, 100, Qt.AlignmentFlag.AlignHCenter, sample.text)
				qp.setPen(sample.color)

							
			# Draw preview pictures
			if sample.picture is not None:
				if sample.picture.size().width() < sample.duration/scale:
					path = QPainterPath()
					path.addRoundedRect(QRectF(t/scale, 40 + self.track_height*sample.track, sample.picture.size().width(), self.track_height), 10, 10)
					qp.setClipPath(path)
					qp.drawPixmap(QRect(t/scale, 40 + self.track_height*sample.track, sample.picture.size().width(), self.track_height), sample.picture)
				else:
					path = QPainterPath()
					path.addRoundedRect(QRectF(t / scale, 40 + self.track_height*sample.track, sample.duration/scale, self.track_height), 10, 10)
					qp.setClipPath(path)
					pic = sample.picture.copy(0, 0, sample.duration/scale, self.track_height)
					qp.drawPixmap(QRect(t / scale, 40 + self.track_height*sample.track, sample.duration/scale, self.track_height), pic)
				
			t += sample.duration

		# Clear clip path
		path = QPainterPath()
		path.addRect(self.rect().x(), self.rect().y(), self.rect().width(), self.rect().height())
		qp.setClipPath(path)

		# Draw pointer
		qp.setPen(QPen(Qt.GlobalColor.black))
		qp.setBrush(QBrush(self.horizontal_line_color))

		qp.drawPolygon(poly)
		qp.setPen(QPen(self.horizontal_line_color))
		qp.drawLine(line)
		qp.end()
   
	# Mouse movement
	def mouseMoveEvent(self, e):
		mapped_x = numpy.interp(e.pos().x(), [0, self.width()], [-self.LEFT_PADDING, self.width() - self.RIGHT_PADDING])
		self.pos = QPoint(mapped_x, e.pos().y())

		# if mouse is being pressed, update pointer
		if self.clicking:
			self.pointerPos = mapped_x
			self.positionChanged.emit(mapped_x)
			self.checkSelection(mapped_x)
			self.pointerTimePos = self.pointerPos*self.getScale()

		self.update()

	# Mouse pressed
	def mousePressEvent(self, e):
		if e.button() == Qt.MouseButton.LeftButton:
			mapped_x = numpy.interp(e.pos().x(), [0, self.width()], [-self.LEFT_PADDING, self.width() - self.RIGHT_PADDING])
			self.pointerPos = mapped_x
			self.positionChanged.emit(mapped_x)
			self.pointerTimePos = self.pointerPos * self.getScale()

			self.checkSelection(mapped_x)

			self.update()
			self.clicking = True  # Set clicking check to true

	# Mouse release
	def mouseReleaseEvent(self, e):
		if e.button() == Qt.MouseButton.LeftButton:
			self.clicking = False  # Set clicking check to false

	# Enter
	def enterEvent(self, e):
		self.is_in = True

	# Leave
	def leaveEvent(self, e):
		self.is_in = False
		self.update()

	# check selection
	def checkSelection(self, x):
		# Did the user click a sample?
		for sample in self.samples:
			if sample.startPos - self.LEFT_PADDING < x < sample.endPos - self.RIGHT_PADDING:
				sample.color = Qt.GlobalColor.darkCyan
				if self.selectedSample is not sample:
					self.selectedSample = sample
					self.selectionChanged.emit(sample)
			else:
				sample.color = sample.defColor

	# Get time string from seconds
	def get_time_string(self, seconds):
		m, s = divmod(seconds, 60)
		h, m = divmod(m, 60)
		return "%02d:%02d:%02d" % (h, m, s)


	# Get scale from length
	def getScale(self):
		return float(self.duration)/float(self.width() - self.LEFT_PADDING - self.RIGHT_PADDING)

	# Get duration
	def getDuration(self):
		return self.duration

	# Get selected sample
	def getSelectedSample(self):
		return self.selectedSample

	# Set background color
	def setBackgroundColor(self, color):
		self.backgroundColor = color

	# Set text color
	def setTextColor(self, color):
		self.textColor = color

	# Set Font
	def setTextFont(self, font):
		self.font = font
