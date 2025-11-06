from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock


class AnimatedEmoji(Widget):
    moisture_level = NumericProperty(50)  # 0-100%
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Store references to graphics instructions
        self.face_color = None
        self.face = None
        self.left_eye = None
        self.right_eye = None
        self.left_eye_color = None
        self.right_eye_color = None
        self.mouth_color = None
        self.mouth = None
        self.tear = None
        self.tear_color = None
        
        # Eye blinking state
        self.is_blinking = False
        self.original_eye_size = 0
        
        self.draw_emoji()
        
        # Bind to update when moisture changes
        self.bind(moisture_level=self.update_expression)
        self.bind(pos=self.redraw, size=self.redraw)
        
        # Start blinking
        Clock.schedule_interval(self.blink, 3)  # Blink every 3 seconds
    
    def get_circle_size(self):
        """Calculate perfect circle size that fits in widget"""
        # Use the smaller dimension to ensure it fits
        size = min(self.width, self.height)
        return size
    
    def get_circle_pos(self):
        """Calculate position to center the circle"""
        size = self.get_circle_size()
        # Center the circle in the widget
        x = self.x + (self.width - size) / 2
        y = self.y + (self.height - size) / 2
        return (x, y)
    
    def draw_emoji(self):
        """Draw the emoji face with all components"""
        self.canvas.clear()
        
        with self.canvas:
            # Get circle dimensions
            circle_size = self.get_circle_size()
            circle_pos = self.get_circle_pos()
            
            # Face (yellow circle) - ALWAYS PERFECT CIRCLE
            self.face_color = Color(1, 0.9, 0.2, 1)  # Yellow
            self.face = Ellipse(
                pos=circle_pos,
                size=(circle_size, circle_size)  # Equal width and height
            )
            
            # Calculate positions based on circle size
            center_x = circle_pos[0] + circle_size / 2
            center_y = circle_pos[1] + circle_size / 2
            self.original_eye_size = circle_size * 0.12
            eye_size = self.original_eye_size
            
            # Left eye
            self.left_eye_color = Color(0, 0, 0, 1)  # Black
            self.left_eye = Ellipse(
                pos=(center_x - circle_size * 0.2 - eye_size/2, 
                     center_y + circle_size * 0.15 - eye_size/2),
                size=(eye_size, eye_size)
            )
            
            # Right eye
            self.right_eye_color = Color(0, 0, 0, 1)  # Black
            self.right_eye = Ellipse(
                pos=(center_x + circle_size * 0.2 - eye_size/2, 
                     center_y + circle_size * 0.15 - eye_size/2),
                size=(eye_size, eye_size)
            )
            
            # Mouth (will be updated based on moisture)
            self.mouth_color = Color(0, 0, 0, 1)  # Black
            self.mouth = Line(points=[], width=3)
            
            # Tear (hidden by default)
            self.tear_color = Color(0.3, 0.6, 1, 0)  # Blue, transparent
            self.tear = Ellipse(
                pos=(center_x + circle_size * 0.2, center_y),
                size=(circle_size * 0.08, circle_size * 0.12)
            )
        
        self.update_expression()
    
    def redraw(self, *args):
        """Redraw when widget is resized or moved"""
        self.draw_emoji()
    
    def blink(self, dt):
        """Make the eyes blink"""
        if self.is_blinking:
            return  # Don't blink if already blinking
        
        self.is_blinking = True
        
        # Get current eye positions
        left_eye_x, left_eye_y = self.left_eye.pos
        right_eye_x, right_eye_y = self.right_eye.pos
        
        # Close eyes (shrink vertically to thin line)
        close_anim = Animation(
            size=(self.original_eye_size, 2),
            pos=(left_eye_x, left_eye_y + self.original_eye_size/2),
            duration=0.1
        )
        close_anim2 = Animation(
            size=(self.original_eye_size, 2),
            pos=(right_eye_x, right_eye_y + self.original_eye_size/2),
            duration=0.1
        )
        
        # Open eyes (return to normal)
        open_anim = Animation(
            size=(self.original_eye_size, self.original_eye_size),
            pos=(left_eye_x, left_eye_y),
            duration=0.1
        )
        open_anim2 = Animation(
            size=(self.original_eye_size, self.original_eye_size),
            pos=(right_eye_x, right_eye_y),
            duration=0.1
        )
        
        # Chain animations: close then open
        sequence = close_anim + open_anim
        sequence2 = close_anim2 + open_anim2
        
        # Reset blinking state when done
        def reset_blink(*args):
            self.is_blinking = False
        sequence.bind(on_complete=reset_blink)
        
        sequence.start(self.left_eye)
        sequence2.start(self.right_eye)
    
    def update_expression(self, *args):
        """Update the emoji expression based on moisture level"""
        circle_size = self.get_circle_size()
        circle_pos = self.get_circle_pos()
        center_x = circle_pos[0] + circle_size / 2
        center_y = circle_pos[1] + circle_size / 2
        mouth_width = circle_size * 0.4
        
        if self.moisture_level > 60:
            # Happy face
            self.draw_happy_mouth(center_x, center_y, mouth_width, circle_size)
            self.animate_face_color((1, 0.9, 0.2, 1))  # Bright yellow
            self.hide_tear()
            
        elif self.moisture_level > 30:
            # Worried face
            self.draw_worried_mouth(center_x, center_y, mouth_width, circle_size)
            self.animate_face_color((1, 0.8, 0.1, 1))  # Darker yellow
            self.hide_tear()
            
        else:
            # Sad face
            self.draw_sad_mouth(center_x, center_y, mouth_width, circle_size)
            self.animate_face_color((0.9, 0.7, 0.1, 1))  # Dull yellow
            self.show_tear(center_x, center_y, circle_size)
    
    def draw_happy_mouth(self, center_x, center_y, width, circle_size):
        """Draw a smiling mouth (curve up)"""
        mouth_y = center_y - circle_size * 0.15
        
        # Create smile using line segments
        num_points = 20
        points = []
        for i in range(num_points):
            x = center_x - width/2 + (width * i / (num_points - 1))
            # Parabola curving down (smile)
            progress = (i / (num_points - 1)) - 0.5
            y = mouth_y - (width/3) * (1 - 4 * progress * progress)
            points.extend([x, y])
        
        self.mouth.points = points
    
    def draw_worried_mouth(self, center_x, center_y, width, circle_size):
        """Draw a straight mouth (neutral)"""
        mouth_y = center_y - circle_size * 0.2
        
        # Straight line
        points = [
            center_x - width/2, mouth_y,
            center_x + width/2, mouth_y
        ]
        self.mouth.points = points
    
    def draw_sad_mouth(self, center_x, center_y, width, circle_size):
        """Draw a frowning mouth (curve down)"""
        mouth_y = center_y - circle_size * 0.15
        
        # Create frown using line segments
        num_points = 20
        points = []
        for i in range(num_points):
            x = center_x - width/2 + (width * i / (num_points - 1))
            # Parabola curving up (frown)
            progress = (i / (num_points - 1)) - 0.5
            y = mouth_y + (width/3) * (1 - 4 * progress * progress)
            points.extend([x, y])
        
        self.mouth.points = points
    
    def animate_face_color(self, target_color):
        """Smoothly change face color"""
        anim = Animation(rgba=target_color, duration=0.8)
        anim.start(self.face_color)
    
    def show_tear(self, center_x, center_y, circle_size):
        """Animate tear appearing"""
        # Reset tear position
        self.tear.pos = (center_x + circle_size * 0.2, center_y)
        self.tear.size = (circle_size * 0.08, circle_size * 0.12)
        
        # Fade in
        anim = Animation(a=1, duration=0.5)
        anim.start(self.tear_color)
        
        # Drop animation
        tear_drop = Animation(
            pos=(self.tear.pos[0], self.tear.pos[1] - circle_size * 0.3),
            duration=1.5,
            t='in_quad'
        )
        tear_drop.start(self.tear)
    
    def hide_tear(self):
        """Hide the tear"""
        anim = Animation(a=0, duration=0.3)
        anim.start(self.tear_color)
    
    def animate_to_level(self, new_level):
        """Animate moisture level change with bounce effect"""
        # Get current circle size
        circle_size = self.get_circle_size()
        
        # Bounce animation for face - maintain perfect circle
        bounce = (
            Animation(size=(circle_size * 1.15, circle_size * 1.15), duration=0.2) +
            Animation(size=(circle_size * 0.95, circle_size * 0.95), duration=0.2) +
            Animation(size=(circle_size, circle_size), duration=0.2)
        )
        bounce.start(self.face)
        
        # Smooth moisture level change
        anim = Animation(moisture_level=new_level, duration=1, t='in_out_quad')
        anim.start(self)


class MoistureIndicator(Widget):
    moisture_level = NumericProperty(0)  # 0-100%
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            # Background (empty container)
            Color(0.3, 0.3, 0.3, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
            # Water level (blue fill)
            Color(0.2, 0.6, 0.9, 1)
            self.water_rect = Rectangle(pos=self.pos, size=(self.width, 0))
            
            # Border
            Color(0.5, 0.5, 0.5, 1)
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=2)
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.bind(moisture_level=self.update_water_level)
    
    def update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border.rectangle = (self.x, self.y, self.width, self.height)
        self.update_water_level()
    
    def update_water_level(self, *args):
        water_height = (self.moisture_level / 100) * self.height
        self.water_rect.pos = self.pos
        self.water_rect.size = (self.width, water_height)
    
    def animate_to_level(self, new_level):
        """Smoothly animate moisture level change"""
        anim = Animation(moisture_level=new_level, duration=1.5, t='in_out_quad')
        anim.start(self)


class AlertLabel(Label):
    def show_alert(self, message, alert_type="warning"):
        """Display animated alert message"""
        self.text = message
        self.opacity = 0
        
        # Color based on alert type
        if alert_type == "critical":
            self.color = (1, 0, 0, 1)
        elif alert_type == "warning":
            self.color = (1, 0.8, 0, 1)
        else:
            self.color = (0, 0.8, 1, 1)
        
        # Fade in animation
        fade_in = Animation(opacity=1, duration=0.5)
        
        # Shake effect for critical alerts
        if alert_type == "critical":
            original_x = self.x
            shake = (Animation(x=self.x + 10, duration=0.1) +
                    Animation(x=self.x - 10, duration=0.1) +
                    Animation(x=original_x, duration=0.1))
            shake.repeat = 2
            fade_in.start(self)
            shake.start(self)
        else:
            fade_in.start(self)


class SmartAgricDashboard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        self.plant_name = "Tomato Plant #1"
        
        # Alert label at top
        self.alert_label = AlertLabel(
            text=f"Monitoring {self.plant_name}",
            size_hint=(1, None),
            height=60,
            font_size='20sp',
            bold=True
        )
        self.add_widget(self.alert_label)
        
        # Main content area - horizontal layout
        content = BoxLayout(orientation='horizontal', size_hint=(1, 1))
        
        # Left side - Moisture bar (takes 25% width)
        moisture_container = BoxLayout(
            orientation='vertical',
            size_hint=(0.25, 1),
            padding=10,
            spacing=10
        )
        
        moisture_label = Label(
            text='Soil Moisture',
            size_hint=(1, None),
            height=30,
            font_size='16sp'
        )
        moisture_container.add_widget(moisture_label)
        
        self.moisture = MoistureIndicator(size_hint=(1, 1))
        moisture_container.add_widget(self.moisture)
        
        self.moisture_text = Label(
            text='50%',
            size_hint=(1, None),
            height=40,
            font_size='24sp',
            bold=True
        )
        moisture_container.add_widget(self.moisture_text)
        
        content.add_widget(moisture_container)
        
        # Center - Emoji (takes 75% width, perfect circle centered)
        emoji_container = FloatLayout(size_hint=(0.75, 1))
        
        # Emoji will be centered and maintain perfect circle
        self.emoji = AnimatedEmoji(
            size_hint=(None, None),
            size=(300, 300),  # Will be adjusted to fit screen
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        emoji_container.add_widget(self.emoji)
        
        content.add_widget(emoji_container)
        
        self.add_widget(content)
        
        # Bottom info bar
        info_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=50,
            padding=10,
            spacing=10
        )
        
        self.status_label = Label(
            text='Status: Monitoring...',
            size_hint=(1, 1),
            font_size='16sp'
        )
        info_bar.add_widget(self.status_label)
        
        self.add_widget(info_bar)
        
        # Bind to window resize to adjust emoji size
        self.bind(size=self.adjust_emoji_size)
        
        # Simulate sensor readings
        Clock.schedule_interval(self.simulate_sensor_update, 5)
    
    def adjust_emoji_size(self, *args):
        """Adjust emoji size to fit screen while maintaining perfect circle"""
        # Calculate appropriate size (70% of available height or width, whichever is smaller)
        available_height = self.height - 110  # Subtract header and footer
        available_width = self.width * 0.75 * 0.9  # 75% width container, 90% of that
        
        # Use smaller dimension to ensure it fits
        size = min(available_height, available_width)
        size = max(size, 100)  # Minimum size of 100
        
        self.emoji.size = (size, size)
    
    def simulate_sensor_update(self, dt):
        """Simulate sensor data updates"""
        import random
        
        # Simulate moisture reading
        moisture = random.randint(20, 95)
        
        # Animate both widgets
        self.moisture.animate_to_level(moisture)
        self.emoji.animate_to_level(moisture)
        
        # Update info
        self.moisture_text.text = f'{moisture}%'
        
        # Update alerts and status
        if moisture < 30:
            self.alert_label.show_alert(
                f"⚠️ {self.plant_name} is TOO DRY! Water needed!",
                alert_type="critical"
            )
            self.status_label.text = 'Status: CRITICAL - Water immediately!'
            self.status_label.color = (1, 0, 0, 1)
        elif moisture < 60:
            self.alert_label.show_alert(
                f"⚡ {self.plant_name} needs attention",
                alert_type="warning"
            )
            self.status_label.text = 'Status: Warning - Water soon'
            self.status_label.color = (1, 0.8, 0, 1)
        else:
            self.alert_label.show_alert(
                f"✓ {self.plant_name} is happy and healthy!",
                alert_type="info"
            )
            self.status_label.text = 'Status: Healthy - All good!'
            self.status_label.color = (0, 0.8, 0.2, 1)


class SmartAgricApp(App):
    def build(self):
        return SmartAgricDashboard()


if __name__ == '__main__':
    SmartAgricApp().run()