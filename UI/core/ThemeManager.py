import customtkinter as ctk


class ThemeManager:
    def __init__(self):
        self.current_theme = "dark"
        self.colors = {
            "dark": {
                "bg": "#1E1E1E",       
                "text": "#E0E0E0",       
                "accent": "#6366F1",      
                "secondary": "#2D2D2D", 
                "drop_area": "#2A2A2A", 
                "border": "#6366F1"       
            },
           "light": {
                "bg": "#858484",
                "text": "#333333",
                "accent": "#8183FC",
                "secondary": "#D1D5DB", 
                "drop_area": "#B0B3B8",  
                "border": "#8183FC"
            }
        }
    
    def set_theme(self, theme):
        self.current_theme = theme.lower()
        ctk.set_appearance_mode(theme)
    
    def get_colors(self):
        return self.colors.get(self.current_theme, self.colors["dark"])
    
    def get_color(self, color_name):
        return self.colors[self.current_theme].get(color_name)