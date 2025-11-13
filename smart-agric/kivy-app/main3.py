from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock

import serial
import json 
import time
from datetime import datetime

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600


def read_sensor_data(ser):
    """Read and parse JSON data from Arduino"""
    try:
        # Read one line from serial
        line = ser.readline().decode("utf-8").strip()
        
        # Skip non-JSON lines (startup messages, etc.)
        if not line.startswith('{'):
            return None
        
        # parse JSON data
        data = json.loads(line)
        return data
    
    except json.JSONDecodeError:
        print("Failed to decode JSON:", line)
        return None
    except UnicodeDecodeError:
        return None
    except Exception as e:
        print("Error reading from serial:", e)
        return None


def save_to_csv(data):
    """Save data as JSON to CSV file for easy parsing later"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # Create a complete data dictionary with timestamp
        log_entry = {
            'timestamp': timestamp,
            'raw': data['raw'],
            'moisture': data['moisture'],
            'temperature': data['temperature'],
            'humidity': data['humidity'],
            'status': data['status']
        }
        
        # Save as JSON string (one JSON object per line)
        with open('sensor_log.jsonl', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        print(f"Saved to log: {log_entry}")
        
    except Exception as e:
        print(f"Error saving to file: {e}")


class AnimatedFace(Widget):
    moisture_level = NumericProperty(50)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Background color (changes based on emotion)
        self.bg_color = None
        self.bg_rect = None
        
        # Graphics references
        self.left_eye = None
        self.right_eye = None
        self.left_eye_color = None
        self.right_eye_color = None
        
        # Eye highlights (for shine effect)
        self.left_eye_highlight = None
        self.right_eye_highlight = None
        
        # Eyebrows
        self.left_brow = None
        self.right_brow = None
        self.left_brow_color = None
        self.right_brow_color = None
        
        # Eyelashes
        self.left_lashes = []
        self.right_lashes = []
        
        # Cheeks
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
            # Background fills entire screen
            self.bg_color = Color(0.85, 0.95, 0.95, 1)  # Light cyan/white
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        with self.canvas:
            # Calculate face area (central 80% of screen)
            face_width = self.width * 0.8
            face_height = self.height * 0.7
            face_x = self.x + (self.width - face_width) / 2
            face_y = self.y + (self.height - face_height) / 2
            
            center_x = self.x + self.width / 2
            center_y = self.y + self.height / 2
            
            # Eye size based on screen
            self.original_eye_size = min(self.width, self.height) * 0.12
            eye_size = self.original_eye_size
            
            # Eye spacing
            eye_spacing = self.width * 0.15
            
            # Eyebrows
            self.left_brow_color = Color(0.2, 0.2, 0.2, 1)
            self.left_brow = Line(points=[], width=5)
            
            self.right_brow_color = Color(0.2, 0.2, 0.2, 1)
            self.right_brow = Line(points=[], width=5)
            
            # Left Eye
            self.left_eye_color = Color(0.1, 0.1, 0.1, 1)
            self.left_eye = Ellipse(
                pos=(center_x - eye_spacing - eye_size/2, 
                     center_y + self.height * 0.08 - eye_size/2),
                size=(eye_size, eye_size)
            )
            
            # Left eye highlight (white shine)
            Color(1, 1, 1, 1)
            self.left_eye_highlight = Ellipse(
                pos=(center_x - eye_spacing - eye_size/2 + eye_size * 0.3, 
                     center_y + self.height * 0.08 - eye_size/2 + eye_size * 0.3),
                size=(eye_size * 0.35, eye_size * 0.35)
            )
            
            # Right Eye
            self.right_eye_color = Color(0.1, 0.1, 0.1, 1)
            self.right_eye = Ellipse(
                pos=(center_x + eye_spacing - eye_size/2, 
                     center_y + self.height * 0.08 - eye_size/2),
                size=(eye_size, eye_size)
            )
            
            # Right eye highlight
            Color(1, 1, 1, 1)
            self.right_eye_highlight = Ellipse(
                pos=(center_x + eye_spacing - eye_size/2 + eye_size * 0.3, 
                     center_y + self.height * 0.08 - eye_size/2 + eye_size * 0.3),
                size=(eye_size * 0.35, eye_size * 0.35)
            )
            
            # Eyelashes
            self.draw_eyelashes(center_x, center_y, eye_spacing, eye_size)
            
            # Cheeks
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
            
            # Mouth
            self.mouth_color = Color(0.2, 0.2, 0.2, 1)
            self.mouth = Line(points=[], width=4)
            
            # Tear
            self.tear_color = Color(0.3, 0.6, 1, 0)
            self.tear = Ellipse(
                pos=(center_x + eye_spacing + eye_size * 0.8, center_y),
                size=(self.width * 0.02, self.height * 0.04)
            )
        
        self.update_expression()
    
    def draw_eyelashes(self, center_x, center_y, eye_spacing, eye_size):
        """Draw eyelashes"""
        lash_length = eye_size * 0.6
        eye_y = center_y + self.height * 0.08 + eye_size/2
        
        # Left eye lashes
        left_eye_x = center_x - eye_spacing
        Color(0.1, 0.1, 0.1, 1)
        for i in range(4):
            offset_x = (i - 1.5) * eye_size * 0.25
            angle_offset = (i - 1.5) * 0.15
            lash = Line(
                points=[
                    left_eye_x + offset_x, eye_y,
                    left_eye_x + offset_x - lash_length * angle_offset, 
                    eye_y + lash_length
                ],
                width=2.5
            )
            self.left_lashes.append(lash)
        
        # Right eye lashes
        right_eye_x = center_x + eye_spacing
        Color(0.1, 0.1, 0.1, 1)
        for i in range(4):
            offset_x = (i - 1.5) * eye_size * 0.25
            angle_offset = (i - 1.5) * 0.15
            lash = Line(
                points=[
                    right_eye_x + offset_x, eye_y,
                    right_eye_x + offset_x + lash_length * angle_offset, 
                    eye_y + lash_length
                ],
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
        
        # Close eyes
        close_anim = Animation(
            size=(self.original_eye_size, 3),
            pos=(left_eye_x, left_eye_y + self.original_eye_size/2),
            duration=0.08
        )
        close_anim2 = Animation(
            size=(self.original_eye_size, 3),
            pos=(right_eye_x, right_eye_y + self.original_eye_size/2),
            duration=0.08
        )
        
        # Hide highlights during blink
        hide_high = Animation(size=(0, 0), duration=0.08)
        hide_high2 = Animation(size=(0, 0), duration=0.08)
        
        # Open eyes
        open_anim = Animation(
            size=(self.original_eye_size, self.original_eye_size),
            pos=(left_eye_x, left_eye_y),
            duration=0.08
        )
        open_anim2 = Animation(
            size=(self.original_eye_size, self.original_eye_size),
            pos=(right_eye_x, right_eye_y),
            duration=0.08
        )
        
        # Show highlights
        show_high = Animation(
            size=(self.original_eye_size * 0.35, self.original_eye_size * 0.35),
            duration=0.08
        )
        show_high2 = Animation(
            size=(self.original_eye_size * 0.35, self.original_eye_size * 0.35),
            duration=0.08
        )
        
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
            # Happy - GREEN BACKGROUND
            self.draw_happy_mouth(center_x, center_y, mouth_width)
            self.draw_happy_eyebrows(center_x, center_y)
            self.animate_background_color((0.3, 0.95, 0.4, 1))  # Bright green
            self.show_cheeks()
            self.hide_tear()
            
        elif self.moisture_level > 30:
            # Worried - YELLOW BACKGROUND
            self.draw_worried_mouth(center_x, center_y, mouth_width)
            self.draw_worried_eyebrows(center_x, center_y)
            self.animate_background_color((1, 0.95, 0.3, 1))  # Bright yellow
            self.hide_cheeks()
            self.hide_tear()
            
        else:
            # Sad - RED BACKGROUND
            self.draw_sad_mouth(center_x, center_y, mouth_width)
            self.draw_sad_eyebrows(center_x, center_y)
            self.animate_background_color((1, 0.4, 0.4, 1))  # Bright red
            self.hide_cheeks()
            self.show_tear(center_x, center_y)
    
    def animate_background_color(self, target_color):
        """Animate the background color change - FASTER"""
        anim = Animation(rgba=target_color, duration=0.3)  # Changed from 1 to 0.3
        anim.start(self.bg_color)
    
    def draw_happy_eyebrows(self, center_x, center_y):
        """Raised, curved eyebrows"""
        eye_spacing = self.width * 0.15
        brow_y = center_y + self.height * 0.18
        brow_width = self.width * 0.08
        
        # Left brow
        left_points = []
        for i in range(8):
            x = center_x - eye_spacing - brow_width/2 + (brow_width * i / 7)
            progress = i / 7
            y = brow_y + self.height * 0.02 * (1 - 4 * (progress - 0.5) ** 2)
            left_points.extend([x, y])
        self.left_brow.points = left_points
        
        # Right brow
        right_points = []
        for i in range(8):
            x = center_x + eye_spacing - brow_width/2 + (brow_width * i / 7)
            progress = i / 7
            y = brow_y + self.height * 0.02 * (1 - 4 * (progress - 0.5) ** 2)
            right_points.extend([x, y])
        self.right_brow.points = right_points
    
    def draw_worried_eyebrows(self, center_x, center_y):
        """Concerned eyebrows"""
        eye_spacing = self.width * 0.15
        brow_y = center_y + self.height * 0.18
        brow_width = self.width * 0.08
        
        # Left brow (slightly raised)
        left_points = [
            center_x - eye_spacing - brow_width/2, brow_y,
            center_x - eye_spacing + brow_width/2, brow_y + self.height * 0.015
        ]
        self.left_brow.points = left_points
        
        # Right brow
        right_points = [
            center_x + eye_spacing - brow_width/2, brow_y + self.height * 0.015,
            center_x + eye_spacing + brow_width/2, brow_y
        ]
        self.right_brow.points = right_points
    
    def draw_sad_eyebrows(self, center_x, center_y):
        """Droopy sad eyebrows"""
        eye_spacing = self.width * 0.15
        brow_y = center_y + self.height * 0.18
        brow_width = self.width * 0.08
        
        # Left brow
        left_points = [
            center_x - eye_spacing - brow_width/2, brow_y,
            center_x - eye_spacing + brow_width/2, brow_y - self.height * 0.02
        ]
        self.left_brow.points = left_points
        
        # Right brow
        right_points = [
            center_x + eye_spacing - brow_width/2, brow_y - self.height * 0.02,
            center_x + eye_spacing + brow_width/2, brow_y
        ]
        self.right_brow.points = right_points
    
    def draw_happy_mouth(self, center_x, center_y, width):
        mouth_y = center_y - self.height * 0.12
        num_points = 20
        points = []
        for i in range(num_points):
            x = center_x - width/2 + (width * i / (num_points - 1))
            progress = (i / (num_points - 1)) - 0.5
            y = mouth_y - (width * 0.4) * (1 - 4 * progress * progress)
            points.extend([x, y])
        self.mouth.points = points
    
    def draw_worried_mouth(self, center_x, center_y, width):
        mouth_y = center_y - self.height * 0.15
        points = [
            center_x - width/2, mouth_y,
            center_x + width/2, mouth_y
        ]
        self.mouth.points = points
    
    def draw_sad_mouth(self, center_x, center_y, width):
        mouth_y = center_y - self.height * 0.12
        num_points = 20
        points = []
        for i in range(num_points):
            x = center_x - width/2 + (width * i / (num_points - 1))
            progress = (i / (num_points - 1)) - 0.5
            y = mouth_y + (width * 0.4) * (1 - 4 * progress * progress)
            points.extend([x, y])
        self.mouth.points = points
    
    def show_cheeks(self):
        """Show rosy cheeks"""
        anim = Animation(a=0.5, duration=0.5)
        anim.start(self.left_cheek_color)
        anim.start(self.right_cheek_color)
    
    def hide_cheeks(self):
        """Hide cheeks"""
        anim = Animation(a=0, duration=0.3)
        anim.start(self.left_cheek_color)
        anim.start(self.right_cheek_color)
    
    def show_tear(self, center_x, center_y):
        eye_spacing = self.width * 0.15
        self.tear.pos = (center_x + eye_spacing + self.original_eye_size * 0.6, center_y)
        
        anim = Animation(a=1, duration=0.5)
        anim.start(self.tear_color)
        
        tear_drop = Animation(
            pos=(self.tear.pos[0], self.tear.pos[1] - self.height * 0.2),
            duration=1.5,
            t='in_quad'
        )
        tear_drop.start(self.tear)
    
    def hide_tear(self):
        anim = Animation(a=0, duration=0.3)
        anim.start(self.tear_color)
    
    def animate_to_level(self, new_level):
        # FASTER animation - changed from 1 to 0.3 seconds
        anim = Animation(moisture_level=new_level, duration=0.3, t='in_out_quad')
        anim.start(self)


class SmartAgricDashboard(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.plant_name = "Tommy"
        
        # Full screen face
        self.face = AnimatedFace(
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        self.add_widget(self.face)
        
        # Top left - Temperature
        temp_display = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(80, 100),
            pos_hint={'x': 0.02, 'top': 0.98}
        )
        
        temp_symbol = Label(
            text='T',
            font_size='50sp',
            bold=True,
            color=(0.9, 0.3, 0.2, 1),
            size_hint=(1, 0.6)
        )
        self.temp_value = Label(
            text='--C',
            font_size='22sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            size_hint=(1, 0.4)
        )
        temp_display.add_widget(temp_symbol)
        temp_display.add_widget(self.temp_value)
        self.add_widget(temp_display)
        
        # Top right - Humidity
        humidity_display = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(80, 100),
            pos_hint={'right': 0.98, 'top': 0.98}
        )
        
        humidity_symbol = Label(
            text='H',
            font_size='50sp',
            bold=True,
            color=(0.2, 0.5, 0.9, 1),
            size_hint=(1, 0.6)
        )
        self.humidity_value = Label(
            text='--%',
            font_size='22sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            size_hint=(1, 0.4)
        )
        humidity_display.add_widget(humidity_symbol)
        humidity_display.add_widget(self.humidity_value)
        self.add_widget(humidity_display)
        
        # Bottom center - Moisture percentage
        self.moisture_label = Label(
            text='--%',
            font_size='56sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            size_hint=(None, None),
            size=(200, 100),
            pos_hint={'center_x': 0.5, 'y': 0.02}
        )
        self.add_widget(self.moisture_label)
        
        # Initialize serial connection ONCE
        self.ser = None
        self.init_serial_connection()
        
        # Read sensor faster - every 0.5 seconds
        Clock.schedule_interval(self.read_sensor_value, 0.5)
    
    def init_serial_connection(self):
        """Initialize serial connection once"""
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            time.sleep(2)  # Wait for Arduino to initialize
            self.ser.flushInput()
            print(f"Connected to {SERIAL_PORT} successfully!")
        except serial.SerialException as e:
            print(f"Error: Could not connect to {SERIAL_PORT}: {e}")
            print("Starting in simulation mode...")
            self.ser = None
    
    def read_sensor_value(self, dt):
        """Read ONE sensor reading per call (non-blocking)"""
        
        # If serial not connected, use simulation
        if self.ser is None:
            self.simulate_sensor_update(dt)
            return
        
        try:
            # Read ONCE - don't loop!
            data = read_sensor_data(self.ser)
            
            if data:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                moisture = data['moisture']
                temperature = data.get('temperature', 0)
                humidity = data.get('humidity', 0)
                
                print(f"[{timestamp}] Raw: {data['raw']:4d} | "
                      f"Moisture: {moisture:3d}% | "
                      f"Temp: {temperature:.1f}C | "
                      f"Humidity: {humidity:.1f}% | "
                      f"Status: {data['status']}")
                
                # Update UI immediately
                self.face.animate_to_level(moisture)
                self.moisture_label.text = str(moisture) + '%'
                self.temp_value.text = str(int(temperature)) + 'C'
                self.humidity_value.text = str(int(humidity)) + '%'
                
                # Save to JSON log
                save_to_csv(data)
                
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            if self.ser:
                self.ser.close()
            self.ser = None
        except Exception as e:
            print(f"Error reading sensor: {e}")
    
    def simulate_sensor_update(self, dt):
        """Fallback simulation mode"""
        import random
        
        moisture = random.randint(20, 95)
        temp = random.randint(18, 30)
        humidity = random.randint(40, 80)
        
        self.face.animate_to_level(moisture)
        
        self.moisture_label.text = str(moisture) + '%'
        self.temp_value.text = str(temp) + 'C'
        self.humidity_value.text = str(humidity) + '%'
    
    def on_stop(self):
        """Clean up serial connection when app closes"""
        if self.ser:
            self.ser.close()
            print("Serial connection closed")


class SmartAgricApp(App):
    def build(self):
        return SmartAgricDashboard()
    
    def on_stop(self):
        """Called when app is closing"""
        self.root.on_stop()
        return True


if __name__ == '__main__':
    SmartAgricApp().run()