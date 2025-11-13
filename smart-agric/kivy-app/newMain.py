from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from supabase import create_client, Client

import serial
import json 
import time
from datetime import datetime
import paho.mqtt.client as mqtt
import json
import time
import random
from threading import Thread
import queue

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

# MQTT Configuration
BROKER = "f3150d0d05ce46d0873bf1a69c56ff38.s1.eu.hivemq.cloud"  # e.g., HiveMQ Cloud URL
PORT = 8883  # Use 8883 for TLS, 1883 for non-TLS
USERNAME = "Ayodeji"
PASSWORD = "cand4f694a@A"
TOPIC = "agripal/farm1/sensor1"

#Device Info
DEVICE_ID = "sensor_1"
FARM_ID = "farm1"



data_queue = queue.Queue()


class SUPABASEPublisher:
    """Upload to Supabase with background thread"""
    
    def __init__(self, url, key):
        self.url = url
        self.key = key
        self.supabase = create_client(self.url, self.key)
        self.queue = queue.Queue()
        self.running = False
        self.upload_thread = None
    
    def start(self):
        """Start background upload thread"""
        self.running = True
        self.upload_thread = Thread(target=self._upload_worker, daemon=True)
        self.upload_thread.start()
        print("Supabase uploader started")
    
    def save_to_supabase(self, data):
        """Save sensor data to Supabase in real-time"""    
        try:
            record = {
                'device_id': DEVICE_ID,
                'farm_id': FARM_ID,
                'timestamp': datetime.now().isoformat(),
                'raw_value': data['raw'],
                'moisture': data['moisture'],
                'temperature': data['temperature'],
                'humidity': data['humidity'],
                'status': data['status']
            }
            
            self.queue.put(record)
        except Exception as e:
            print(f"Supabase error: {e}")
    
    def _upload_worker(self):
        """Background worker that uploads batches"""
        batch = []
        while self.running:
            try:
                timeout = time.time() + 30
                while len(batch) < 20 and time.time() < timeout:
                    try:
                        record = self.queue.get(timeout=1)
                        batch.append(record)
                    except queue.Empty:
                        continue
                
                if batch:
                    self.supabase.table('sensor_readings').insert(batch).execute()
                    print(f"Uploaded {len(batch)} records")
                    batch = []
            
            except Exception as e:
                print(f"Upload error: {e}")
                time.sleep(5)
    
    def stop(self):
        """Stop uploader and flush remaining data"""
        self.running = False
        
        remaining = []
        while not self.queue.empty():
            try:
                remaining.append(self.queue.get_nowait())
            except queue.Empty:
                break
        
        if remaining:
            try:
                self.supabase.table('sensor_readings').insert(remaining).execute()
                print(f"Flished {len(remaining)} records")
            except Exception as e:
                print(f"Final flush failed: {e}")
                        
class MQTTPublisher:
    """Seperate class to manage MQTT connection"""
    def __init__(self):
        self.client = None
        self.connected = False
        self.setup_client()
    
    def setup_client(self):
        """Initialize MQTT client with proper callbacks"""
        self.client = mqtt.Client(
            client_id=f"raspberry_pi_{DEVICE_ID}",
            callback_api_version = mqtt.CallbackAPIVersion.VERSION2,
            protocol=mqtt.MQTTv5
        ) 
        
        self.client.username_pw_set(USERNAME, PASSWORD)
        self.client.tls_set()
        
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish

    def on_connect(self, client, userdata, flags, reason_code, properties):
        """Callback when connected"""
        if reason_code == 0:
            print("Connected to MQTT Broker")
            self.connected = True
        else:
            print(f"Failed to connect, return code {reason_code}")
            self.connected = False
    
    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        """Callback when disconnected"""
        print(f"Disconnected from MQTT Broker (code: {reason_code})")
        self.connected = False
    
    def on_publish(self, client, userdata, mid, reason_code, properties):
        """Callback when message is published"""
        print(f"Message {mid} published")
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(BROKER, PORT, keepalive=60)
            self.client.loop_start()
            
            timeout = 5
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            return self.connected
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def publish(self, temperature, humidity, moisture):
        """Publish sensor data to MQTT"""
        if not self.connected:
            print("Not connected to MQTT broker")
            return False
        
        try:
            sensor_data = {
                "device_id": DEVICE_ID,
                "farm_id": FARM_ID,
                "timestamp": int(time.time()),
                "soil_moisture": float(moisture),
                "temperature": float(temperature),
                "humidity": float(humidity),
                "ph_level": 7.0,
                "nitrogen": 100.0
            }
            
            payload = json.dumps(sensor_data)
            result = self.client.publish(TOPIC, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"Published M:{moisture}% T:{temperature}C H:{humidity}%")
                return True
            else:
                print(f"Publish failed with code: {result.rc}")
                return False
        
        except Exception as e:
            print(f"Failed to publish sensor data: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            print("Disconnected from MQTT")      

class SerialReader:
    """Separate class to handle serial communication"""
    
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.running = False
    
    def connect(self):
        """Connect to serial port"""
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=2)
            time.sleep(2)  # Wait for Arduino to initialize
            self.serial.flushInput()
            print(f"✅ Connected to serial port: {self.port}")
            return True
        except serial.SerialException as e:
            print(f"❌ Could not connect to {self.port}: {e}")
            return False
    
    def read_data(self):
        """Read and parse JSON data from Arduino"""
        try:
            line = self.serial.readline().decode("utf-8").strip()
            
            if not line.startswith('{'):
                return None
            
            data = json.loads(line)
            return data
        
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return None
        except UnicodeDecodeError:
            return None
        except Exception as e:
            print(f"❌ Error reading from serial: {e}")
            return None
    
    def start_reading(self, data_queue):
        """Start reading in a separate thread"""
        self.running = True
        
        def read_loop():
            while self.running:
                data = self.read_data()
                if data:
                    data_queue.put(data)
                time.sleep(0.1)
        
        thread = Thread(target=read_loop, daemon=True)
        thread.start()
    
    def stop(self):
        """Stop reading and close serial port"""
        self.running = False
        if self.serial:
            self.serial.close()
            print("👋 Serial port closed")
      

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

# def save_to_csv(data):
#     """Save data to CSV file for logging"""
#     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
#     try:
#         with open('sensor_log.csv', 'a') as f:
#             f.write(f"{timestamp},{data['raw']},{data['moisture']},{data['temperature']},{data['humidity']},{data['status']}\n")
#     except Exception as e:
#         print(f"❌ Error saving to CSV: {e}")

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
        left_high_x, left_high_y = self.left_eye_highlight.pos
        right_high_x, right_high_y = self.right_eye_highlight.pos
        
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
        """Animate the background color change"""
        anim = Animation(rgba=target_color, duration=0.5)
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
        anim = Animation(moisture_level=new_level, duration=1, t='in_out_quad')
        anim.start(self)


class SmartAgricDashboard(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.plant_name = "Tommy"
        
        # Initialize MQTT and Serial
        self.mqtt_publisher = MQTTPublisher()
        self.serial_reader = SerialReader(SERIAL_PORT, BAUD_RATE)
        self.supabase = SUPABASEPublisher(SUPABASE_URL, SUPABASE_KEY)
        self.supabase.start()
        
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
            text='24C',
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
            text='65%',
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
            text='50%',
            font_size='56sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            size_hint=(None, None),
            size=(200, 100),
            pos_hint={'center_x': 0.5, 'y': 0.02}
        )
        self.add_widget(self.moisture_label)
        
        # Start simulation
        # Clock.schedule_interval(self.simulate_sensor_update, 5)
        
        # Connect to MQTT
        Clock.schedule_once(self.initialize_connections, 1)
        
        Clock.schedule_interval(self.check_sensor_data, 0.5)
    
    def initialize_connections(self, dt):
        """Initialize MQTT and Serial connections"""
        # connect to MQTT
        if self.mqtt_publisher.connect():
            print("MQTT ready")
        else:
            print("MQTT connection failed")
        
        # Connect to Serial and start reading
        if self.serial_reader.connect():
            self.serial_reader.start_reading(data_queue)
            print("Serial reader started")
        else:
          print("Serial connection failed")
    
    def check_sensor_data(self, dt):
        """Check queue for new sensor data (non-blocking)"""
        try:
            data = data_queue.get_nowait()
            
            if data:
                moisture = data.get('moisture', 0)
                temperature = data.get('temperature', 0)
                humidity = data.get('humidity', 0)
                
                self.face.animate_to_level(moisture)
                self.moisture_label.text = f"{moisture}%"
                self.temp_value.text = f"{temperature}°C"
                self.humidity_value.text = f"{humidity}%"
                
                # Publish to MQTT
                self.mqtt_publisher.publish(temperature, humidity, moisture)
                self.supabase.save_to_supabase(data)
                
                # Save to CSV
                save_to_csv(data)
                
                # Log
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"[{timestamp}] Moisture: {moisture}% | Temp: {temperature}°C | Humidity: {humidity}%")
            
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Error processing sensor data: {e}")
    
    def on_stop(self):
        """Cleanup when app closes"""
        self.serial_reader.stop()
        self.mqtt_publisher.disconnect()
        self.supabase.stop()
            
                    


class SmartAgricApp(App):
    def build(self):
        return SmartAgricDashboard()

    def on_stop(self):
        """Called when app is closing"""
        self.dashboard.on_stop()
        return True

if __name__ == '__main__':
    try:
        SmartAgricApp().run()
    except KeyboardInterrupt:
        print("\n Shutting down....")
    
    