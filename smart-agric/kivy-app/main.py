from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy_garden.graph import Graph, MeshLinePlot

import serial
import json 
import time
import os
from datetime import datetime

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600


def read_sensor_data(ser):
    """Read and parse JSON data from Arduino"""
    try:
        line = ser.readline().decode("utf-8").strip()
        if not line.startswith('{'):
            return None
        data = json.loads(line)
        return data
    except:
        return None


def save_to_csv(data):
    """Save data as JSON to file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        log_entry = {
            'timestamp': timestamp,
            'raw': data['raw'],
            'moisture': data['moisture'],
            'temperature': data.get('temperature', 0),
            'humidity': data.get('humidity', 0),
            'status': data['status']
        }
        
        with open('sensor_log.jsonl', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
    except Exception as e:
        print(f"Error saving: {e}")


def load_sensor_data(filename='sensor_log.jsonl'):
    """Load sensor data from JSON lines file"""
    data = []
    
    if not os.path.exists(filename):
        return generate_sample_data()
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    data.append(entry)
                except:
                    continue
        
        return data if data else generate_sample_data()
    except:
        return generate_sample_data()


def generate_sample_data():
    """Generate sample data"""
    import random
    from datetime import datetime, timedelta
    
    data = []
    start_time = datetime.now() - timedelta(hours=24)
    
    for i in range(100):
        timestamp = start_time + timedelta(minutes=i * 15)
        moisture = 40 + random.randint(-20, 40)
        temp = 25 + random.randint(-5, 10)
        humidity = 50 + random.randint(-15, 25)
        
        data.append({
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'raw': random.randint(300, 700),
            'moisture': max(0, min(100, moisture)),
            'temperature': temp,
            'humidity': max(0, min(100, humidity)),
            'status': 'WET' if moisture > 60 else ('MOIST' if moisture > 30 else 'DRY')
        })
    
    return data


def analyze_data(data):
    """Analyze sensor data and generate insights"""
    if not data:
        return {
            'avg_moisture': 0, 'avg_temp': 0, 'avg_humidity': 0,
            'min_moisture': 0, 'max_moisture': 0, 'dry_periods': 0,
            'total_readings': 0,
            'insights': ["No data available yet!"]
        }
    
    moistures = [d['moisture'] for d in data]
    temps = [d['temperature'] for d in data]
    humidities = [d['humidity'] for d in data]
    
    avg_moisture = sum(moistures) / len(moistures)
    avg_temp = sum(temps) / len(temps)
    avg_humidity = sum(humidities) / len(humidities)
    
    dry_periods = sum(1 for m in moistures if m < 30)
    
    insights = []
    
    if avg_moisture < 40:
        insights.append(f"WARNING: Low moisture ({avg_moisture:.1f}%). Water more frequently!")
    elif avg_moisture > 70:
        insights.append(f"HIGH moisture ({avg_moisture:.1f}%). Reduce watering.")
    else:
        insights.append(f"OPTIMAL moisture ({avg_moisture:.1f}%). Great job!")
    
    if dry_periods > len(data) * 0.3:
        insights.append(f"{dry_periods} critical dry periods detected!")
    
    if avg_temp > 30:
        insights.append(f"High temperature ({avg_temp:.1f}C). Consider shade.")
    elif avg_temp < 18:
        insights.append(f"Low temperature ({avg_temp:.1f}C). Protect from cold.")
    
    insights.append(f"Monitored {len(data)} data points.")
    
    return {
        'avg_moisture': avg_moisture, 'avg_temp': avg_temp,
        'avg_humidity': avg_humidity, 'min_moisture': min(moistures),
        'max_moisture': max(moistures), 'dry_periods': dry_periods,
        'total_readings': len(data), 'insights': insights
    }


class AnimatedFace(Widget):
    moisture_level = NumericProperty(50)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = None
        self.bg_rect = None
        self.left_eye = None
        self.right_eye = None
        self.left_eye_color = None
        self.right_eye_color = None
        self.left_eye_highlight = None
        self.right_eye_highlight = None
        self.left_brow = None
        self.right_brow = None
        self.left_brow_color = None
        self.right_brow_color = None
        self.left_lashes = []
        self.right_lashes = []
        self.left_cheek = None
        self.right_cheek = None
        self.left_cheek_color = None
        self.right_cheek_color = None
        self.mouth_color = None
        self.mouth = None
        self.tear = None
        self.tear_color = None
        self.is_blinking = False
        self.original_eye_size = 0
        
        self.draw_face()
        self.bind(moisture_level=self.update_expression)
        self.bind(pos=self.redraw, size=self.redraw)
        Clock.schedule_interval(self.blink, 3)
    
    def draw_face(self):
        self.canvas.clear()
        
        with self.canvas.before:
            self.bg_color = Color(0.85, 0.95, 0.95, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        with self.canvas:
            center_x = self.x + self.width / 2
            center_y = self.y + self.height / 2
            self.original_eye_size = min(self.width, self.height) * 0.12
            eye_size = self.original_eye_size
            eye_spacing = self.width * 0.15
            
            self.left_brow_color = Color(0.2, 0.2, 0.2, 1)
            self.left_brow = Line(points=[], width=5)
            self.right_brow_color = Color(0.2, 0.2, 0.2, 1)
            self.right_brow = Line(points=[], width=5)
            
            self.left_eye_color = Color(0.1, 0.1, 0.1, 1)
            self.left_eye = Ellipse(
                pos=(center_x - eye_spacing - eye_size/2, 
                     center_y + self.height * 0.08 - eye_size/2),
                size=(eye_size, eye_size)
            )
            
            Color(1, 1, 1, 1)
            self.left_eye_highlight = Ellipse(
                pos=(center_x - eye_spacing - eye_size/2 + eye_size * 0.3, 
                     center_y + self.height * 0.08 - eye_size/2 + eye_size * 0.3),
                size=(eye_size * 0.35, eye_size * 0.35)
            )
            
            self.right_eye_color = Color(0.1, 0.1, 0.1, 1)
            self.right_eye = Ellipse(
                pos=(center_x + eye_spacing - eye_size/2, 
                     center_y + self.height * 0.08 - eye_size/2),
                size=(eye_size, eye_size)
            )
            
            Color(1, 1, 1, 1)
            self.right_eye_highlight = Ellipse(
                pos=(center_x + eye_spacing - eye_size/2 + eye_size * 0.3, 
                     center_y + self.height * 0.08 - eye_size/2 + eye_size * 0.3),
                size=(eye_size * 0.35, eye_size * 0.35)
            )
            
            self.draw_eyelashes(center_x, center_y, eye_spacing, eye_size)
            
            cheek_size = self.width * 0.08
            self.left_cheek_color = Color(1, 0.7, 0.75, 0)
            self.left_cheek = Ellipse(
                pos=(center_x - self.width * 0.25 - cheek_size/2, 
                     center_y - self.height * 0.05 - cheek_size/2),
                size=(cheek_size, cheek_size * 0.7)
            )
            
            self.right_cheek_color = Color(1, 0.7, 0.75, 0)
            self.right_cheek = Ellipse(
                pos=(center_x + self.width * 0.25 - cheek_size/2, 
                     center_y - self.height * 0.05 - cheek_size/2),
                size=(cheek_size, cheek_size * 0.7)
            )
            
            self.mouth_color = Color(0.2, 0.2, 0.2, 1)
            self.mouth = Line(points=[], width=4)
            
            self.tear_color = Color(0.3, 0.6, 1, 0)
            self.tear = Ellipse(
                pos=(center_x + eye_spacing + eye_size * 0.8, center_y),
                size=(self.width * 0.02, self.height * 0.04)
            )
        
        self.update_expression()
    
    def draw_eyelashes(self, center_x, center_y, eye_spacing, eye_size):
        lash_length = eye_size * 0.6
        eye_y = center_y + self.height * 0.08 + eye_size/2
        
        left_eye_x = center_x - eye_spacing
        Color(0.1, 0.1, 0.1, 1)
        for i in range(4):
            offset_x = (i - 1.5) * eye_size * 0.25
            angle_offset = (i - 1.5) * 0.15
            lash = Line(
                points=[left_eye_x + offset_x, eye_y,
                       left_eye_x + offset_x - lash_length * angle_offset, 
                       eye_y + lash_length],
                width=2.5
            )
            self.left_lashes.append(lash)
        
        right_eye_x = center_x + eye_spacing
        Color(0.1, 0.1, 0.1, 1)
        for i in range(4):
            offset_x = (i - 1.5) * eye_size * 0.25
            angle_offset = (i - 1.5) * 0.15
            lash = Line(
                points=[right_eye_x + offset_x, eye_y,
                       right_eye_x + offset_x + lash_length * angle_offset, 
                       eye_y + lash_length],
                width=2.5
            )
            self.right_lashes.append(lash)
    
    def redraw(self, *args):
        self.draw_face()
    
    def blink(self, dt):
        if self.is_blinking:
            return
        
        self.is_blinking = True
        
        left_eye_x, left_eye_y = self.left_eye.pos
        right_eye_x, right_eye_y = self.right_eye.pos
        
        close_anim = Animation(size=(self.original_eye_size, 3),
                              pos=(left_eye_x, left_eye_y + self.original_eye_size/2),
                              duration=0.08)
        close_anim2 = Animation(size=(self.original_eye_size, 3),
                               pos=(right_eye_x, right_eye_y + self.original_eye_size/2),
                               duration=0.08)
        hide_high = Animation(size=(0, 0), duration=0.08)
        hide_high2 = Animation(size=(0, 0), duration=0.08)
        
        open_anim = Animation(size=(self.original_eye_size, self.original_eye_size),
                             pos=(left_eye_x, left_eye_y), duration=0.08)
        open_anim2 = Animation(size=(self.original_eye_size, self.original_eye_size),
                              pos=(right_eye_x, right_eye_y), duration=0.08)
        show_high = Animation(size=(self.original_eye_size * 0.35, self.original_eye_size * 0.35),
                             duration=0.08)
        show_high2 = Animation(size=(self.original_eye_size * 0.35, self.original_eye_size * 0.35),
                              duration=0.08)
        
        sequence = close_anim + open_anim
        sequence2 = close_anim2 + open_anim2
        high_seq = hide_high + show_high
        high_seq2 = hide_high2 + show_high2
        
        def reset_blink(*args):
            self.is_blinking = False
        sequence.bind(on_complete=reset_blink)
        
        sequence.start(self.left_eye)
        sequence2.start(self.right_eye)
        high_seq.start(self.left_eye_highlight)
        high_seq2.start(self.right_eye_highlight)
    
    def update_expression(self, *args):
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        mouth_width = self.width * 0.25
        
        if self.moisture_level > 60:
            self.draw_happy_mouth(center_x, center_y, mouth_width)
            self.draw_happy_eyebrows(center_x, center_y)
            self.animate_background_color((0.3, 0.95, 0.4, 1))
            self.show_cheeks()
            self.hide_tear()
        elif self.moisture_level > 30:
            self.draw_worried_mouth(center_x, center_y, mouth_width)
            self.draw_worried_eyebrows(center_x, center_y)
            self.animate_background_color((1, 0.95, 0.3, 1))
            self.hide_cheeks()
            self.hide_tear()
        else:
            self.draw_sad_mouth(center_x, center_y, mouth_width)
            self.draw_sad_eyebrows(center_x, center_y)
            self.animate_background_color((1, 0.4, 0.4, 1))
            self.hide_cheeks()
            self.show_tear(center_x, center_y)
    
    def animate_background_color(self, target_color):
        Animation(rgba=target_color, duration=0.3).start(self.bg_color)
    
    def draw_happy_eyebrows(self, center_x, center_y):
        eye_spacing = self.width * 0.15
        brow_y = center_y + self.height * 0.18
        brow_width = self.width * 0.08
        
        left_points = []
        for i in range(8):
            x = center_x - eye_spacing - brow_width/2 + (brow_width * i / 7)
            progress = i / 7
            y = brow_y + self.height * 0.02 * (1 - 4 * (progress - 0.5) ** 2)
            left_points.extend([x, y])
        self.left_brow.points = left_points
        
        right_points = []
        for i in range(8):
            x = center_x + eye_spacing - brow_width/2 + (brow_width * i / 7)
            progress = i / 7
            y = brow_y + self.height * 0.02 * (1 - 4 * (progress - 0.5) ** 2)
            right_points.extend([x, y])
        self.right_brow.points = right_points
    
    def draw_worried_eyebrows(self, center_x, center_y):
        eye_spacing = self.width * 0.15
        brow_y = center_y + self.height * 0.18
        brow_width = self.width * 0.08
        
        self.left_brow.points = [
            center_x - eye_spacing - brow_width/2, brow_y,
            center_x - eye_spacing + brow_width/2, brow_y + self.height * 0.015
        ]
        self.right_brow.points = [
            center_x + eye_spacing - brow_width/2, brow_y + self.height * 0.015,
            center_x + eye_spacing + brow_width/2, brow_y
        ]
    
    def draw_sad_eyebrows(self, center_x, center_y):
        eye_spacing = self.width * 0.15
        brow_y = center_y + self.height * 0.18
        brow_width = self.width * 0.08
        
        self.left_brow.points = [
            center_x - eye_spacing - brow_width/2, brow_y,
            center_x - eye_spacing + brow_width/2, brow_y - self.height * 0.02
        ]
        self.right_brow.points = [
            center_x + eye_spacing - brow_width/2, brow_y - self.height * 0.02,
            center_x + eye_spacing + brow_width/2, brow_y
        ]
    
    def draw_happy_mouth(self, center_x, center_y, width):
        mouth_y = center_y - self.height * 0.12
        points = []
        for i in range(20):
            x = center_x - width/2 + (width * i / 19)
            progress = (i / 19) - 0.5
            y = mouth_y - (width * 0.4) * (1 - 4 * progress * progress)
            points.extend([x, y])
        self.mouth.points = points
    
    def draw_worried_mouth(self, center_x, center_y, width):
        mouth_y = center_y - self.height * 0.15
        self.mouth.points = [center_x - width/2, mouth_y, center_x + width/2, mouth_y]
    
    def draw_sad_mouth(self, center_x, center_y, width):
        mouth_y = center_y - self.height * 0.12
        points = []
        for i in range(20):
            x = center_x - width/2 + (width * i / 19)
            progress = (i / 19) - 0.5
            y = mouth_y + (width * 0.4) * (1 - 4 * progress * progress)
            points.extend([x, y])
        self.mouth.points = points
    
    def show_cheeks(self):
        Animation(a=0.5, duration=0.5).start(self.left_cheek_color)
        Animation(a=0.5, duration=0.5).start(self.right_cheek_color)
    
    def hide_cheeks(self):
        Animation(a=0, duration=0.3).start(self.left_cheek_color)
        Animation(a=0, duration=0.3).start(self.right_cheek_color)
    
    def show_tear(self, center_x, center_y):
        eye_spacing = self.width * 0.15
        self.tear.pos = (center_x + eye_spacing + self.original_eye_size * 0.6, center_y)
        Animation(a=1, duration=0.5).start(self.tear_color)
        Animation(pos=(self.tear.pos[0], self.tear.pos[1] - self.height * 0.2),
                 duration=1.5, t='in_quad').start(self.tear)
    
    def hide_tear(self):
        Animation(a=0, duration=0.3).start(self.tear_color)
    
    def animate_to_level(self, new_level):
        Animation(moisture_level=new_level, duration=0.3, t='in_out_quad').start(self)


class MainMonitorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = FloatLayout()
        
        self.face = AnimatedFace(size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        layout.add_widget(self.face)
        
        # Analytics button
        analytics_btn = Button(
            text='View Analytics',
            size_hint=(None, None),
            size=(180, 60),
            pos_hint={'center_x': 0.5, 'y': 0.45},
            background_color=(0.3, 0.6, 0.9, 0.9),
            bold=True,
            font_size='18sp'
        )
        analytics_btn.bind(on_press=self.go_to_analytics)
        layout.add_widget(analytics_btn)
        
        # Temperature
        temp_layout = BoxLayout(orientation='vertical', size_hint=(None, None),
                               size=(80, 100), pos_hint={'x': 0.02, 'top': 0.98})
        temp_layout.add_widget(Label(text='T', font_size='50sp', bold=True,
                                    color=(0.9, 0.3, 0.2, 1), size_hint=(1, 0.6)))
        self.temp_value = Label(text='--C', font_size='22sp', bold=True,
                               color=(0.2, 0.2, 0.2, 1), size_hint=(1, 0.4))
        temp_layout.add_widget(self.temp_value)
        layout.add_widget(temp_layout)
        
        # Humidity
        humid_layout = BoxLayout(orientation='vertical', size_hint=(None, None),
                                size=(80, 100), pos_hint={'right': 0.98, 'top': 0.98})
        humid_layout.add_widget(Label(text='H', font_size='50sp', bold=True,
                                     color=(0.2, 0.5, 0.9, 1), size_hint=(1, 0.6)))
        self.humidity_value = Label(text='--%', font_size='22sp', bold=True,
                                   color=(0.2, 0.2, 0.2, 1), size_hint=(1, 0.4))
        humid_layout.add_widget(self.humidity_value)
        layout.add_widget(humid_layout)
        
        # Moisture
        self.moisture_label = Label(text='--%', font_size='56sp', bold=True,
                                   color=(0.2, 0.2, 0.2, 1), size_hint=(None, None),
                                   size=(200, 100), pos_hint={'center_x': 0.5, 'y': 0.02})
        layout.add_widget(self.moisture_label)
        
        self.add_widget(layout)
        
        # Serial connection
        self.ser = None
        self.init_serial()
        Clock.schedule_interval(self.read_sensor, 0.5)
    
    def init_serial(self):
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            time.sleep(2)
            self.ser.flushInput()
            print("Connected!")
        except:
            print("Simulation mode")
            self.ser = None
    
    def read_sensor(self, dt):
        if self.ser is None:
            self.simulate_data(dt)
            return
        
        try:
            data = read_sensor_data(self.ser)
            if data:
                moisture = data['moisture']
                self.face.animate_to_level(moisture)
                self.moisture_label.text = str(moisture) + '%'
                self.temp_value.text = str(int(data.get('temperature', 0))) + 'C'
                self.humidity_value.text = str(int(data.get('humidity', 0))) + '%'
                save_to_csv(data)
        except:
            pass
    
    def simulate_data(self, dt):
        import random
        m = random.randint(20, 95)
        self.face.animate_to_level(m)
        self.moisture_label.text = str(m) + '%'
        self.temp_value.text = str(random.randint(18, 30)) + 'C'
        self.humidity_value.text = str(random.randint(40, 80)) + '%'
    
    def go_to_analytics(self, *args):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'analytics'
    
    def on_stop(self):
        if self.ser:
            self.ser.close()


class AnalyticsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        with layout.canvas.before:
            Color(0.95, 0.97, 1, 1)
            self.bg = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=lambda *a: setattr(self.bg, 'pos', layout.pos),
                   size=lambda *a: setattr(self.bg, 'size', layout.size))
        
        # Header
        header = BoxLayout(size_hint=(1, None), height=70, spacing=10)
        back_btn = Button(text='Back', size_hint=(None, 1), width=100,
                         background_color=(0.3, 0.7, 0.9, 1), bold=True)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        header.add_widget(Label(text='Data Analytics', font_size='28sp', bold=True,
                               color=(0.2, 0.2, 0.2, 1)))
        refresh_btn = Button(text='Refresh', size_hint=(None, 1), width=100,
                            background_color=(0.3, 0.9, 0.5, 1), bold=True)
        refresh_btn.bind(on_press=self.load_data)
        header.add_widget(refresh_btn)
        layout.add_widget(header)
        
        # Scroll
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, padding=10)
        content.bind(minimum_height=content.setter('height'))
        
        # Stats
        stats = BoxLayout(size_hint=(1, None), height=100, spacing=10)
        self.moisture_card = self.create_card('Moisture', '--', (0.2, 0.7, 0.9, 1))
        self.temp_card = self.create_card('Temp', '--', (0.9, 0.4, 0.3, 1))
        self.humid_card = self.create_card('Humidity', '--', (0.5, 0.8, 0.4, 1))
        stats.add_widget(self.moisture_card)
        stats.add_widget(self.temp_card)
        stats.add_widget(self.humid_card)
        content.add_widget(stats)
        
        # Graphs
        for title in ['All Parameters', 'Temperature vs Moisture', 'Humidity vs Moisture']:
            graph_box = BoxLayout(size_hint=(1, None), height=300, padding=10)
            with graph_box.canvas.before:
                Color(1, 1, 1, 0.9)
                rect = Rectangle(pos=graph_box.pos, size=graph_box.size)
            graph_box.bind(pos=lambda i,v,r=rect: setattr(r, 'pos', i.pos),
                          size=lambda i,v,r=rect: setattr(r, 'size', i.size))
            
            graph_layout = BoxLayout(orientation='vertical')
            graph_layout.add_widget(Label(text=title, size_hint=(1, None), height=30,
                                        font_size='18sp', bold=True))
            
            graph = Graph(xlabel='X', ylabel='Y', x_ticks_major=20, y_ticks_major=20,
                         x_grid=True, y_grid=True, xmin=0, xmax=100, ymin=0, ymax=100)
            graph_layout.add_widget(graph)
            graph_box.add_widget(graph_layout)
            content.add_widget(graph_box)
            
            if title == 'All Parameters':
                self.graph1 = graph
            elif title == 'Temperature vs Moisture':
                self.graph2 = graph
            else:
                self.graph3 = graph
        
        # Insights
        insights_box = BoxLayout(orientation='vertical', size_hint=(1, None), padding=15, spacing=10)
        insights_box.bind(minimum_height=insights_box.setter('height'))
        with insights_box.canvas.before:
            Color(0.95, 0.98, 0.95, 1)
            self.insights_bg = Rectangle(pos=insights_box.pos, size=insights_box.size)
        insights_box.bind(pos=lambda *a: setattr(self.insights_bg, 'pos', insights_box.pos),
                         size=lambda *a: setattr(self.insights_bg, 'size', insights_box.size))
        
        insights_box.add_widget(Label(text='Smart Insights', font_size='22sp', bold=True,
                                     color=(0.2, 0.5, 0.2, 1), size_hint=(1, None), height=40))
        
        self.insights_label = Label(text='Loading...', font_size='16sp',
                                   color=(0.3, 0.3, 0.3, 1), size_hint=(1, None),
                                   markup=True, halign='left', valign='top')
        self.insights_label.bind(texture_size=lambda *a: setattr(self.insights_label, 'height',
                                                                 self.insights_label.texture_size[1] + 20))
        self.insights_label.bind(size=self.insights_label.setter('text_size'))
        insights_box.add_widget(self.insights_label)
        content.add_widget(insights_box)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
        
        self.bind(on_enter=lambda *a: self.load_data())
    
    def create_card(self, label, value, color):
        card = BoxLayout(orientation='vertical', padding=10)
        with card.canvas.before:
            Color(*color)
            card.bg = Rectangle(pos=card.pos, size=card.size)
        card.bind(pos=lambda *a: setattr(card.bg, 'pos', card.pos),
                 size=lambda *a: setattr(card.bg, 'size', card.size))
        
        card.add_widget(Label(text=label, font_size='16sp', color=(1,1,1,0.9)))
        value_label = Label(text=value, font_size='28sp', bold=True, color=(1,1,1,1))
        card.add_widget(value_label)
        card.value_label = value_label
        return card
    
    def load_data(self, *args):
        data = load_sensor_data()
        analysis = analyze_data(data)
        
        self.moisture_card.value_label.text = f"{analysis['avg_moisture']:.1f}%"
        self.temp_card.value_label.text = f"{analysis['avg_temp']:.1f}C"
        self.humid_card.value_label.text = f"{analysis['avg_humidity']:.1f}%"
        
        display_data = data[-100:]
        
        # Graph 1: All parameters
        moisture_plot = MeshLinePlot(color=[0.2, 0.6, 0.9, 1])
        moisture_plot.points = [(i, d['moisture']) for i, d in enumerate(display_data)]
        
        temp_plot = MeshLinePlot(color=[0.9, 0.4, 0.2, 1])
        temp_plot.points = [(i, d['temperature'] * 2) for i, d in enumerate(display_data)]
        
        humid_plot = MeshLinePlot(color=[0.4, 0.8, 0.4, 1])
        humid_plot.points = [(i, d['humidity']) for i, d in enumerate(display_data)]
        
        for p in list(self.graph1.plots):
            self.graph1.remove_plot(p)
        self.graph1.add_plot(moisture_plot)
        self.graph1.add_plot(temp_plot)
        self.graph1.add_plot(humid_plot)
        
        # Graph 2: Temp vs Moisture
        temp_moisture_plot = MeshLinePlot(color=[0.9, 0.4, 0.2, 1])
        temp_moisture_plot.points = [(d['temperature'], d['moisture']) for d in display_data]
        
        for p in list(self.graph2.plots):
            self.graph2.remove_plot(p)
        self.graph2.xmin = min(d['temperature'] for d in display_data) - 2
        self.graph2.xmax = max(d['temperature'] for d in display_data) + 2
        self.graph2.add_plot(temp_moisture_plot)
        
        # Graph 3: Humidity vs Moisture
        humid_moisture_plot = MeshLinePlot(color=[0.4, 0.8, 0.4, 1])
        humid_moisture_plot.points = [(d['humidity'], d['moisture']) for d in display_data]
        
        for p in list(self.graph3.plots):
            self.graph3.remove_plot(p)
        self.graph3.add_plot(humid_moisture_plot)
        
        # Insights
        self.insights_label.text = '\n\n'.join(analysis['insights'])
    
    def go_back(self, *args):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'


class SmartAgricApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMonitorScreen(name='main'))
        sm.add_widget(AnalyticsScreen(name='analytics'))
        return sm
    
    def on_stop(self):
        if hasattr(self.root.get_screen('main'), 'on_stop'):
            self.root.get_screen('main').on_stop()
        return True


if __name__ == '__main__':
    SmartAgricApp().run()