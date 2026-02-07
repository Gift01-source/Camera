#!/usr/bin/env python3
"""
🎥 AI Camera Mobile App - Python Kivy Version
Builds to native APK for Android phones
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.garden.navigationdrawer import NavigationDrawer
from kivy.clock import Clock
from kivy.uix.popup import Popup
import requests
import json
from datetime import datetime

# CHANGE THIS TO YOUR IP
API_URL = "http://10.0.2.78:5000"

class CameraApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "🎥 AI Camera"
        self.status_data = {}
        self.events_data = []
        
    def build(self):
        self.root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = Label(
            text="🎥 AI Camera\nReal-time Security",
            size_hint_y=0.15,
            font_size='24sp',
            bold=True
        )
        self.root.add_widget(header)
        
        # Scrollable content
        scroll = ScrollView(size_hint=(1, 0.75))
        content = GridLayout(cols=1, spacing=5, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Status section
        self.status_label = Label(
            text="📊 Loading status...",
            size_hint_y=None,
            height=100,
            markup=True
        )
        content.add_widget(self.status_label)
        
        # Events section
        self.events_label = Label(
            text="🚨 Recent Events",
            size_hint_y=None,
            height=200,
            markup=True
        )
        content.add_widget(self.events_label)
        
        scroll.add_widget(content)
        self.root.add_widget(scroll)
        
        # Refresh button
        refresh_btn = Button(
            text="🔄 Refresh",
            size_hint_y=0.1
        )
        refresh_btn.bind(on_press=self.refresh_data)
        self.root.add_widget(refresh_btn)
        
        # Start auto-refresh
        Clock.schedule_interval(self.auto_refresh, 5)
        
        # Initial load
        self.refresh_data()
        
        return self.root
    
    def refresh_data(self, *args):
        """Fetch data from API"""
        try:
            # Fetch status
            status_res = requests.get(f"{API_URL}/api/status", timeout=5)
            self.status_data = status_res.json()
            
            # Fetch events
            events_res = requests.get(f"{API_URL}/api/events", timeout=5)
            self.events_data = events_res.json()
            
            self.update_ui()
        except Exception as e:
            self.status_label.text = f"❌ Error: {str(e)}\n\nMake sure API is running at:\n{API_URL}"
    
    def auto_refresh(self, dt):
        """Auto-refresh every 5 seconds"""
        self.refresh_data()
    
    def update_ui(self):
        """Update UI with fetched data"""
        # Update status
        if self.status_data:
            status = self.status_data.get('status', 'unknown')
            fps = self.status_data.get('fps', 0)
            frames = self.status_data.get('frames_processed', 0)
            
            status_text = f"""
[b]📊 System Status[/b]
Status: {status.upper()}
FPS: {fps}
Frames: {frames}
API: {API_URL}
            """.strip()
            
            self.status_label.text = status_text
        
        # Update events
        if self.events_data:
            events_text = "[b]🚨 Recent Events[/b]\n\n"
            for event in self.events_data[:5]:
                event_type = event.get('type', 'unknown')
                severity = event.get('severity', 'unknown')
                timestamp = event.get('timestamp', '')
                
                # Format timestamp
                if timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp = dt.strftime('%H:%M:%S')
                
                events_text += f"{event_type} [{severity}] {timestamp}\n"
            
            self.events_label.text = events_text
        else:
            self.events_label.text = "[b]🚨 Recent Events[/b]\n\nNo events yet"

if __name__ == '__main__':
    CameraApp().run()
