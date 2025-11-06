from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.core.window import Window

class AnimatedEmoji(Widget):
    moisture_level = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.face_color = None
        self.face = None
        self.left_eye = None
        self.right_eye = None
        self.left_eye_color = None
        self.right_eye_color = None
        self.mouth = None
        self.mouth_color = None
        self.tear = None
        self.tear_color = None
        
        # Eye blinking state
        self.is_blinking = False
        self.original_eye_size = 0
        
        self.draw_emoji()
        
        # When moisture_level changes → update_expression runs
        self.bind(moisture_level=self.update_expression)
        # When position or size changes → redraw runs
        self.bind(pos=self.redraw, size=self.redraw)
        
        Clock.schedule_interval(self.blink, 3)
    
    def get_circle_size(self):
        """Calculate perfect circle size that fits in widget"""
        
        size = min(self.width, self.height)
        return size
    
    def get_circle_pos(self):
        """Calculate position to center the circle"""
        size = self.get_circle_size()
        
        # Centre the circle in the widget
        x = self.x + (self.width - size) / 2
        y = self.y + (self.height - size) / 2
        return (x, y)
    
    def draw_emoji(self):
        """Draw the emoji face and features"""
        self.canvas.clear()
        with self.canvas:
            # Get circle dimensions
            circle_size = self.get_circle_size()
            circle_pos = self.get_circle_pos()
            self.face_color = Color(1, 0.9, 0.2, 1)
            self.face = Ellipse(
                pos = circle_pos,
                size = (circle_size, circle_size)
            )
            center_x = circle_pos[0] + circle_size / 2
            # Center X = 50 + 300/2 = 50 + 150 = 200
            center_y = circle_pos[1] + circle_size / 2
            # Center Y = 50 + 300/2 = 50 + 150 = 200
            self.original_eye_size = circle_size * 0.12
            eye_size = self.original_eye_size
            
            # Left eye
            self.left_eye_color = Color(0, 0, 0, 1)
            self.left_eye = Ellipse(
                pos = (center_x - circle_size * 0.2 - eye_size / 2,
                       center_y + circle_size * 0.15 - eye_size / 2),
                size = (eye_size, eye_size)
            )
            
            # Right eye
            self.right_eye_color = Color(0, 0, 0, 1) # Black
            self.right_eye = Ellipse(
                pos = (center_x + circle_size * 0.2 - eye_size / 2,
                       center_y + circle_size * 0.15 - eye_size / 2),
                size = (eye_size, eye_size)
            )
            
            """"
            Left eye X-position:
            = center_x - circle_size × 0.2 - eye_size/2
            = 200 - 300×0.2 - 36/2
            = 200 - 60 - 18
            = 122

            Left eye Y-position:
            = center_y + circle_size × 0.15 - eye_size/2
            = 200 + 300×0.15 - 36/2
            = 200 + 45 - 18
            = 227

            """
            self.mouth_color = Color(0, 0, 0, 1)
            self.mouth = Line(points=[], width=3)
            
            self.tear_color = Color(0.3, 0.6, 1, 0 )
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
                return 
            self.is_blinking = True
                
            left_eye_x, left_eye_y = self.left_eye.pos
            right_eye_x, right_eye_y = self.right_eye.pos
                
            close_anim = Animation(
                size = (self.original_eye_size, 2),
                pos = (left_eye_x, left_eye_y + self.original_eye_size / 2),
                duration = 0.1
            )
                
            close_anim2 = Animation(
                size = (self.original_eye_size, 2),
                pos = (left_eye_x, left_eye_y + self.original_eye_size / 2),
                duration = 0.1
            )    
                
            open_anim = Animation(
                size = (self.original_eye_size, self.original_eye_size),
                pos = (left_eye_x, left_eye_y),
                duration = 0.1
            )
                
            open_anim2 = Animation(
                size = (self.original_eye_size, self.original_eye_size),
                pos = (right_eye_x, right_eye_y),
                duration = 0.1
            )
                
            sequence = close_anim + open_anim
            sequence2 = close_anim2 + open_anim2
            
            # Reset blinking state when done
            def reset_blink(*args):
                self.is_blinking = False
            sequence.bind(on_complete=reset_blink)
            
            sequence.start(self.left_eye)
            sequence2.start(self.right_eye)
    
    def update_expression(self, *args):
        """Update the emoji expression based on mositure level
        """
        circle_size = self.get_circle_size()
        circle_pos = self.get_circle_pos()
        center_x = circle_pos[0] + circle_size / 2
        center_y = circle_pos[1] + circle_size / 2
        mouth_width = circle_pos * 0.4
        
        if self.moisture_level > 60:
            # Happy face
            self.draw_happy_mouth(center_x, center_y, mouth_width, circle_size)
            self.animate_face_color((1, 0.9, 0.2, 1)) # Bright Yellow
            self.hide_tear()
            
        elif self.moisture_level > 30:
            # Worried face
            self.draw_worried_mount(center_x, center_y, mouth_width, circle_size)
            self.animate_face_color((1, 0.8, 0.1, 1)) # Darker yellow
            self.hide_tear()
        
        else:
            # Sad face
            self.draw_sad_mouth(center_x, center_y, mouth_width, circle_size)
            self.animate_face_color((0.9, 0.7, 0.1, 1))
            self.show_tear(center_x, center_y, circle_size)
    
    def draw_happy_mouth(self, center_x, center_y, width, circle_size):
        """Draw a smiling mouth (curve up)"""
        mouth_y = center_y - circle_size * 0.15
        
        # Create smile using line segments
        num_points = 20
        points = []
        for i in range(num_points):
            x = center_x - width / 2 + (width * i / (num_points - 1))
            """
            **Breaking this down:**
            ```
            Let's say:
            center_x = 200
            width = 120
            num_points = 20

            When i = 0 (first point):
            x = 200 - 120/2 + (120 × 0 / 19)
            x = 200 - 60 + 0
            x = 140  ← Left edge of mouth

            When i = 10 (middle point):
            x = 200 - 60 + (120 × 10 / 19)
            x = 200 - 60 + 63.16
            x = 203.16  ← Near center

            When i = 19 (last point):
            x = 200 - 60 + (120 × 19 / 19)
            x = 200 - 60 + 120
            x = 260  ← Right edge of mouth
            """
            # Parabola curving down (smile)
            progress = (i / (num_points - 1)) - 0.5
            y = mouth_y - (width / 3) * (1 - 4 * progress * progress)
            points.extend([x, y])
        
        self.mouth.points = points
    
    def draw_worried_mouth(self, center_x, center_y, width, circle_size):
        """Draw a straight mouth (neutral)"""
        mouth_y = center_y - circle_size * 0.2
        
        # Straight line
        
        points = [
            center_x - width / 2, mouth_y,
            center_x + width / 2, mouth_y
        ]
        """
        Breaking this doen
        Let's say
        center_x = 200
        width = 120
        centre_y = 200
        circle_size = 300
        
        mouth_y = 200 - 300 * 0.2
        mouth_y = 200 - 60
        mouth_y = 140
        
        therefore mouth_y will be drawn at 140 on the Y-axis
        
        why 0.2 (20%)? because a neutral mouth is lower than a smile but higher than a sad mouth
        """
        self.mouth.points = points
    
    def draw_sad_mouth(self, center_x, center_y, width, circle_size):
        """Draw a frowning mouth (curve down)"""
        mouth_y = center_y - circle_size * 0.15
        
        # Create frown using line segments
        num_points = 20
        points = []
        for i in range(num_points):
            x = center_x - width / 2 + (width * i / (num_points - 1))
            
            # Parabola curvin up (frown)
            
            num_points = 20
            points = []
            for i in range(num_points):
                x = center_x - width / 2 + (width * i / (num_points - 1))
                # Paraboal curving up (frown)
                progress = (i / (num_points - 1)) - 0.5
                y = mouth_y + (width / 3) * (1 - 4 * progress * progress)
                points.extend([x, y])
            
            self.mouth.points = points
    
    def animate_face_color(self, target_color):
        """Smoothly animate face color to target_color"""
        anim = Animation(
            rgba=target_color, duration=0.8)
        anim.start(self.face_color)
        
        """
                Animation(rgba=target_color, duration=0.8)
        #         ↑                  ↑
        #    Property to change   Time in seconds
        ```

        **What's rgba?**
        - Red, Green, Blue, Alpha values
        - `self.face_color` is a Color object
        - Color objects have an `rgba` property we can animate

        **Example transition:**
        ```
        Current: (1.0, 0.9, 0.2, 1)  ← Bright yellow
        Target:  (0.9, 0.7, 0.1, 1)  ← Dull yellow

        Animation smoothly transitions:
        Time 0.0s: (1.0, 0.9, 0.2, 1)
        Time 0.2s: (0.975, 0.85, 0.175, 1)
        Time 0.4s: (0.95, 0.8, 0.15, 1)
        Time 0.6s: (0.925, 0.75, 0.125, 1)
        Time 0.8s: (0.9, 0.7, 0.1, 1)  ← Reaches target
        """
    
    def show_tear(self, center_x, center_y, circle_size):
        """Animate tear appearing"""
        # REset tear position
        
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
        anim = Animation(
            moisture_level=new_level,
            duration=1.0,
            t='out_quad'
        )
        anim.start(self)

class MoistureIndicator(Widget):
    moisture_level = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            #Background (empty conatiner)
            Color(0.3, 0.3, 0.3, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
            # Water level (blue fill)
            Color(0.5, 0.6, 0.9, 1 )
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
        """ Smoothly animate moisture level change """
        anim = Animation(moisture_level=new_level, duration=1.5, t='in_out_quad')
        anim.start(self)

class AlertLabel(Label):
    def show_alert(self, message, alert_type="warnings"):
        """Display animated alert message"""
        self.text = message
        self.opacity = 0
        
        # Color based on alert type
        if alert_type == "warning":
            target_color = (1, 0, 0, 1)
        elif alert_type == "warning":
            self.color = (1, 0.8, 0, 1)
        else:
            self.color = (0, 0.8, 1, 1)
        
        # Fade in animation
        fade_in = Animation(opacity=1, duration=0.5)
        
        # Shake effect for critical alerts 
        if alert_type == "critical":
            original_x = self.x
            shake = (
                Animation(x=self.x + 10, duration=0.1) +
                Animation(x=self.x - 10, duration=0.1) +
                Animation(x=original_x, duration=0.1)
            )
            shake.repeat = 2
            fade_in.start(self)
            shake.start(self)
        else:
            fade_in.start(self)
        
                
                