from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock

class MoistureIndicator(Widget):
    moisture_level = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.3, 0.3, 0.3, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
            Color(0.2, 0.6, 0.9, 1)
            self.water_rect = Rectangle(pos=self.pos, size=(self.width, 0))
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.bind(moisture_level=self.update_water_level)
    
    def update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.update_water_level()
    
    def update_water_level(self, *args):
        water_height = (self.moisture_level / 100) * self.height
        self.water_rect.pos = self.pos
        self.water_rect.size = (self.width, water_height)
    
    def animate_to_level(self, new_level):
        """Smoothly animate moisture level change."""
        anim = Animation(moisture_level=new_level, duration=1.5, t='in_out_quad')
        anim.start(self)
            
class PlantHealthIndicator(Widget):
    health_status = StringProperty("healthy")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self.color = Color(0, 1, 0, 1)
            self.plant_icon = Ellipse(pos=self.pos, size=self.size)
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.bind(health_status=self.update_status)
    
    def update_graphics(self, *args):
        self.plant_icon.pos = self.pos
        self.plant_icon.size = self.size
    
    def update_status(self, *args):
        """Change color and pulse based on health status."""
        if self.health_status == "healthy":
            target_color = (0, 1, 0, 1)
        elif self.health_status == "warning":
            target_color = (1, 0.8, 0, 1)
            self.pulse_animation()
        elif self.health_status == "critical":
            target_color = (1, 0, 0, 1)
            self.pulse_animation()
        
        # Animate color change
        anim = Animation(rgba=target_color, duration=0.5)
        anim.start(self.color)
        
    def pulse_animation(self):
        """Pulsing effect for warnings"""
        anim = (Animation(size=(self.width * 1.2, self.height * 1.2), duration=0.5) +
                Animation(size=(self.width, self.height), duration=0.5))
        anim.repeat = True
        anim.start(self)
    
class AlertLabel(Label):
    def show_alert(self, message, alert_type="warnings"):
        """Display animated alert message"""
        self.text = message
        self.opacity = 0
        
        if alert_type == "critical":
            self.color = (1, 0, 0, 1)
        elif alert_type == "warning":
            self.color = (1, 0.8, 0, 1)
        else:
            self.color = (0, 0.8, 1, 1)
        
        fade_in = Animation(opacity=1, duration=0.5)
        
        if alert_type == "critical":
            shake = (Animation(x=self.x + 10, duration=0.1) +
                     Animation(x=self.x - 10, duration=0.1) +
                        Animation(x=self.x, duration=0.1))
            shake.repeat = 2
            fade_in.start(self)
            shake.start(self)
        else:
            fade_in.start(self)

class SmartAgricDashboard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        self.plant_name = "Tomato Plant #1"
        self.alert_label = AlertLabel(
            text=f"Monitoring {self.plant_name}", size_hint=(1, 0.2), font_size='20sp'
        )
        self.add_widget(self.alert_label)
        
        self.moisture = MoistureIndicator(size_hint=(0.3, 0.6))
        self.add_widget(self.moisture)
        
        self.health = PlantHealthIndicator(size_hint=(0.2, 0.2))
        self.add_widget(self.health)
        
        Clock.schedule_interval(self.simulate_data_update, 5)
    
    def simulate_data_update(self, dt):
        """Simulate sensor data updates."""
        import random 
        
        moisture = random.randint(20, 80)
        self.moisture.animate_to_level(moisture)
        
        if moisture < 30:
            self.health.health_status = "critical"
            self.alert_label.show_alert(f"{self.plant_name} is TOO DRY! Water needed!", alert_type="critical")
        
        elif moisture < 50:
            self.health.health_status = "warning"
            self.alert_label.show_alert(f"{self.plant_name} moisture is LOW. Consider watering.", alert_type="warning")
        
        else:
            self.health.health_status = "healthy"
            self.alert_label.show_alert(f"{self.plant_name} is healthy.", alert_type="info")

class SmartAgricApp(App):
    def build(self):
        return SmartAgricDashboard()

if __name__ == '__main__':
    SmartAgricApp().run()
    