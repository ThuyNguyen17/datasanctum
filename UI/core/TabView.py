import customtkinter as ctk

class TabView(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        segmented_button_font = kwargs.pop("segmented_button_font", ctk.CTkFont(weight="bold"))
        segmented_button_selected_color = kwargs.pop("segmented_button_selected_color", "#9597FF")
        segmented_button_selected_hover_color = kwargs.pop("segmented_button_selected_hover_color", "#534BF3")
        segmented_button_unselected_color = kwargs.pop("segmented_button_unselected_color", ("#A7A7A7", "#E0E0E0"))
        segmented_button_unselected_hover_color = kwargs.pop("segmented_button_unselected_hover_color", ("#9E9E9E", "#D1D5DB"))

        super().__init__(master, **kwargs)
        self._segmented_button.configure(
            selected_color=segmented_button_selected_color,
            selected_hover_color=segmented_button_selected_hover_color,
            unselected_color=segmented_button_unselected_color,
            unselected_hover_color=segmented_button_unselected_hover_color,
            text_color=("#E0E0E0", "#333333"),
            font=segmented_button_font
        )