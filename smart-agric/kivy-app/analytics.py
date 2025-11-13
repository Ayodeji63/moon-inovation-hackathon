from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.image import Image as KivyImage
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.properties import NumericProperty
from kivy.clock import Clock

import serial
import json 
import time
import os
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
from kivy.core.image import Image as CoreImage

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600


def read_sensor_data(ser):
    try:
        line = ser.readline().decode("utf-8").strip()
        if not line.startswith('{'):
            return None
        return json.loads(line)
    except:
        return None


def save_to_csv(data):
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
    data = []
    if not os.path.exists(filename):
        return generate_sample_data()
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                try:
                    data.append(json.loads(line.strip()))
                except:
                    continue
        return data if data else generate_sample_data()
    except:
        return generate_sample_data()


def generate_sample_data():
    import random
    from datetime import datetime, timedelta
    
    data = []
    start_time = datetime.now() - timedelta(hours=24)
    
    for i in range(100):
        timestamp = start_time + timedelta(minutes=i * 15)
        moisture = 40 + random.randint(-20, 40)
        data.append({
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'raw': random.randint(300, 700),
            'moisture': max(0, min(100, moisture)),
            'temperature': 25 + random.randint(-5, 10),
            'humidity': 50 + random.randint(-15, 25),
            'status': 'WET' if moisture > 60 else ('MOIST' if moisture > 30 else 'DRY')
        })
    return data


def analyze_data(data):
    if not data:
        return {
            'avg_moisture': 0, 'avg_temp': 0, 'avg_humidity': 0,
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
        insights.append(f"WARNING: Low moisture ({avg_moisture:.1f}%)")
    elif avg_moisture > 70:
        insights.append(f"HIGH moisture ({avg_moisture:.1f}%)")
    else:
        insights.append(f"OPTIMAL moisture ({avg_moisture:.1f}%)")
    
    if dry_periods > len(data) * 0.3:
        insights.append(f"{dry_periods} critical dry periods!")
    
    if avg_temp > 30:
        insights.append(f"High temp ({avg_temp:.1f}C)")
    elif avg_temp < 18:
        insights.append(f"Low temp ({avg_temp:.1f}C)")
    
    insights.append(f"Total: {len(data)} readings")
    
    return {
        'avg_moisture': avg_moisture,
        'avg_temp': avg_temp,
        'avg_humidity': avg_humidity,
        'insights': insights
    }


def create_graph_image(data, graph_type='all'):
    display_data = data[-100:]
    fig, ax = plt.subplots(figsize=(8, 5), facecolor='white')
    
    if graph_type == 'all':
        times = list(range(len(display_data)))
        ax.plot(times, [d['moisture'] for d in display_data], 'b-', linewidth=2, label='Moisture')
        ax.plot(times, [d['temperature'] for d in display_data], 'r-', linewidth=2, label='Temp')
        ax.plot(times, [d['humidity'] for d in display_data], 'g-', linewidth=2, label='Humidity')
        ax.set_title('All Parameters Over Time', fontsize=14, fontweight='bold')
        ax.legend()
    elif graph_type == 'temp_moisture':
        temps = [d['temperature'] for d in display_data]
        moistures = [d['moisture'] for d in display_data]
        ax.scatter(temps, moistures, c='red', s=30, alpha=0.6)
        ax.set_xlabel('Temperature (°C)', fontsize=12)
        ax.set_ylabel('Moisture (%)', fontsize=12)
        ax.set_title('Temperature vs Moisture', fontsize=14, fontweight='bold')
    else:
        humids = [d['humidity'] for d in display_data]
        moistures = [d['moisture'] for d in display_data]
        ax.scatter(humids, moistures, c='green', s=30, alpha=0.6)
        ax.set_xlabel('Humidity (%)', fontsize=12)
        ax.set_ylabel('Moisture (%)', fontsize=12)
        ax.set_title('Humidity vs Moisture', fontsize=14, fontweight='bold')
    
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=80)
    buf.seek(0)
    texture = CoreImage(buf, ext='png').texture
    plt.close(fig)
    return texture


class AnimatedFace(Widget):
    moisture_level = NumericProperty(50)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = None
        self.bg_rect = None
        self.left_eye = None
        self.right_eye = None
        self.left_eye_highlight = None
        self.right_eye_highlight = None
        self.left_brow = None
        self.right_brow = None
        self.left_cheek_color = None
        self.right_cheek_color = None
        self.mouth = None
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
            
            Color(0.2, 0.2, 0.2, 1)
            self.left_brow = Line(points=[], width=5)
            self.right_brow = Line(points=[], width=5)
            
            Color(0.1, 0.1, 0.1, 1)
            self.left_eye = Ellipse(
                pos=(center_x - eye_spacing - eye_size/2, center_y + self.height * 0.08 - eye_size/2),
                size=(eye_size, eye_size)
            )
            Color(1, 1, 1, 1)
            self.left_eye_highlight = Ellipse(
                pos=(center_x - eye_spacing - eye_size/2 + eye_size * 0.3, 
                     center_y + self.height * 0.08 - eye_size/2 + eye_size * 0.3),
                size=(eye_size * 0.35, eye_size * 0.35)
            )
            
            Color(0.1, 0.1, 0.1, 1)
            self.right_eye = Ellipse(
                pos=(center_x + eye_spacing - eye_size/2, center_y + self.height * 0.08 - eye_size/2),
                size=(eye_size, eye_size)
            )
            Color(1, 1, 1, 1)
            self.right_eye_highlight = Ellipse(
                pos=(center_x + eye_spacing - eye_size/2 + eye_size * 0.3, 
                     center_y + self.height * 0.08 - eye_size/2 + eye_size * 0.3),
                size=(eye_size * 0.35, eye_size * 0.35)
            )
            
            # Eyelashes
            Color(0.1, 0.1, 0.1, 1)
            for pos_x in [center_x - eye_spacing, center_x + eye_spacing]:
                for i in range(4):
                    offset = (i - 1.5) * eye_size * 0.25
                    Line(points=[pos_x + offset, center_y + self.height * 0.08 + eye_size/2,
                                pos_x + offset, center_y + self.height * 0.08 + eye_size/2 + eye_size * 0.6],
                        width=2)
            
            cheek_size = self.width * 0.08
            self.left_cheek_color = Color(1, 0.7, 0.75, 0)
            Ellipse(pos=(center_x - self.width * 0.25 - cheek_size/2, 
                        center_y - self.height * 0.05 - cheek_size/2),
                   size=(cheek_size, cheek_size * 0.7))
            
            self.right_cheek_color = Color(1, 0.7, 0.75, 0)
            Ellipse(pos=(center_x + self.width * 0.25 - cheek_size/2, 
                        center_y - self.height * 0.05 - cheek_size/2),
                   size=(cheek_size, cheek_size * 0.7))
            
            Color(0.2, 0.2, 0.2, 1)
            self.mouth = Line(points=[], width=4)
            
            self.tear_color = Color(0.3, 0.6, 1, 0)
            Ellipse(pos=(center_x + eye_spacing + eye_size * 0.8, center_y),
                   size=(self.width * 0.02, self.height * 0.04))
        
        self.update_expression()
    
    def redraw(self, *args):
        self.draw_face()
    
    def blink(self, dt):
        if self.is_blinking:
            return
        self.is_blinking = True
        
        left_eye_x, left_eye_y = self.left_eye.pos
        right_eye_x, right_eye_y = self.right_eye.pos
        
        close = Animation(size=(self.original_eye_size, 3),
                         pos=(left_eye_x, left_eye_y + self.original_eye_size/2), duration=0.08)
        open_a = Animation(size=(self.original_eye_size, self.original_eye_size),
                          pos=(left_eye_x, left_eye_y), duration=0.08)
        
        def reset(*args):
            self.is_blinking = False
        (close + open_a).bind(on_complete=reset).start(self.left_eye)
        (close + open_a).start(self.right_eye)
    
    def update_expression(self, *args):
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        mouth_width = self.width * 0.25
        
        if self.moisture_level > 60:
            self.draw_happy_mouth(center_x, center_y, mouth_width)
            Animation(rgba=(0.3, 0.95, 0.4, 1), duration=0.3).start(self.bg_color)
            Animation(a=0.5, duration=0.5).start(self.left_cheek_color)
            Animation(a=0.5, duration=0.5).start(self.right_cheek_color)
        elif self.moisture_level > 30:
            self.draw_worried_mouth(center_x, center_y, mouth_width)
            Animation(rgba=(1, 0.95, 0.3, 1), duration=0.3).start(self.bg_color)
            Animation(a=0, duration=0.3).start(self.left_cheek_color)
        else:
            self.draw_sad_mouth(center_x, center_y, mouth_width)
            Animation(rgba=(1, 0.4, 0.4, 1), duration=0.3).start(self.bg_color)
    
    def draw_happy_mouth(self, cx, cy, w):
        points = []
        for i in range(20):
            x = cx - w/2 + (w * i / 19)
            y = cy - self.height * 0.12 - (w * 0.4) * (1 - 4 * ((i/19) - 0.5) ** 2)
            points.extend([x, y])
        self.mouth.points = points
    
    def draw_worried_mouth(self, cx, cy, w):
        self.mouth.points = [cx - w/2, cy - self.height * 0.15, cx + w/2, cy - self.height * 0.15]
    
    def draw_sad_mouth(self, cx, cy, w):
        points = []
        for i in range(20):
            x = cx - w/2 + (w * i / 19)
            y = cy - self.height * 0.12 + (w * 0.4) * (1 - 4 * ((i/19) - 0.5) ** 2)
            points.extend([x, y])
        self.mouth.points = points
    
    def animate_to_level(self, new_level):
        Animation(moisture_level=new_level, duration=0.3, t='in_out_quad').start(self)


class MainMonitorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = FloatLayout()
        
        self.face = AnimatedFace(size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        layout.add_widget(self.face)
        
        # Analytics button - BOTTOM CENTER
        analytics_btn = Button(
            text='View Analytics Dashboard',
            size_hint=(None, None),
            size=(250, 60),
            pos_hint={'center_x': 0.5, 'y': 0.05},  # Bottom position
            background_color=(0.3, 0.6, 0.9, 0.95),
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
        
        # Moisture - TOP CENTER
        self.moisture_label = Label(text='--%', font_size='56sp', bold=True,
                                   color=(0.2, 0.2, 0.2, 1), size_hint=(None, None),
                                   size=(200, 100), pos_hint={'center_x': 0.5, 'top': 0.95})
        layout.add_widget(self.moisture_label)
        
        self.add_widget(layout)
        
        self.ser = None
        self.init_serial()
        Clock.schedule_interval(self.read_sensor, 0.5)
    
    def init_serial(self):
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            time.sleep(2)
            self.ser.flushInput()
        except:
            self.ser = None
    
    def read_sensor(self, dt):
        if self.ser is None:
            import random
            m = random.randint(20, 95)
            self.face.animate_to_level(m)
            self.moisture_label.text = str(m) + '%'
            self.temp_value.text = str(random.randint(18, 30)) + 'C'
            self.humidity_value.text = str(random.randint(40, 80)) + '%'
            return
        
        try:
            data = read_sensor_data(self.ser)
            if data:
                m = data['moisture']
                self.face.animate_to_level(m)
                self.moisture_label.text = str(m) + '%'
                self.temp_value.text = str(int(data.get('temperature', 0))) + 'C'
                self.humidity_value.text = str(int(data.get('humidity', 0))) + '%'
                save_to_csv(data)
        except:
            pass
    
    def go_to_analytics(self, *args):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'analytics'


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
        back_btn = Button(text='< Back', size_hint=(None, 1), width=100,
                         background_color=(0.3, 0.7, 0.9, 1), bold=True, font_size='18sp')
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        header.add_widget(Label(text='Data Analytics', font_size='28sp', bold=True,
                               color=(0.2, 0.2, 0.2, 1)))
        refresh_btn = Button(text='Refresh', size_hint=(None, 1), width=100,
                            background_color=(0.3, 0.9, 0.5, 1), bold=True, font_size='18sp')
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
        for title in ['all', 'temp_moisture', 'humid_moisture']:
            graph_box = BoxLayout(size_hint=(1, None), height=300, padding=10)
            with graph_box.canvas.before:
                Color(1, 1, 1, 0.9)
                rect = Rectangle(pos=graph_box.pos, size=graph_box.size)
            graph_box.bind(pos=lambda i,v,r=rect: setattr(r, 'pos', i.pos),
                          size=lambda i,v,r=rect: setattr(r, 'size', i.size))
            
            img = KivyImage(allow_stretch=True)
            graph_box.add_widget(img)
            content.add_widget(graph_box)
            
            if title == 'all':
                self.graph1_img = img
            elif title == 'temp_moisture':
                self.graph2_img = img
            else:
                self.graph3_img = img
        
        # Insights - FIXED to prevent layout loop
        insights_box = BoxLayout(orientation='vertical', size_hint=(1, None), height=200, padding=15)
        with insights_box.canvas.before:
            Color(0.95, 0.98, 0.95, 1)
            r = Rectangle(pos=insights_box.pos, size=insights_box.size)
        insights_box.bind(pos=lambda *a: setattr(r, 'pos', insights_box.pos),
                         size=lambda *a: setattr(r, 'size', insights_box.size))
        
        insights_box.add_widget(Label(text='Smart Insights', font_size='22sp', bold=True,
                                     color=(0.2, 0.5, 0.2, 1), size_hint=(1, None), height=40))
        
        # FIX: Simple label with fixed height - no auto-sizing
        self.insights_label = Label(
            text='Loading...',
            font_size='16sp',
            color=(0.3, 0.3, 0.3, 1),
            size_hint=(1, 1)  # Takes remaining space
        )
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
        
        # Generate graphs
        self.graph1_img.texture = create_graph_image(data, 'all')
        self.graph2_img.texture = create_graph_image(data, 'temp_moisture')
        self.graph3_img.texture = create_graph_image(data, 'humid_moisture')
        
        # Insights - simple text join
        self.insights_label.text = '\n'.join(analysis['insights'])
    
    def go_back(self, *args):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'


class SmartAgricApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMonitorScreen(name='main'))
        sm.add_widget(AnalyticsScreen(name='analytics'))
        return sm


if __name__ == '__main__':
    SmartAgricApp().run()