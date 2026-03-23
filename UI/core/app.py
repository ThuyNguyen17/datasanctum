import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import filedialog, ttk, messagebox
import os
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from core.TabView import TabView
from core.LanguageManager import LanguageManager
from core.ThemeManager import ThemeManager
from core.RecentFilesManager import RecentFilesManager
from core.FileProcessor import FileProcessor
from customtkinter import CTkImage
import json
import numpy as np
from sklearn.decomposition import PCA


class FileAnalyzerApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("DataSanctum - File Analyzer")
        self.geometry("1400x900")
        self.minsize(1100, 800)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Setup managers
        self.language_manager = LanguageManager(self)
        self.theme_manager = ThemeManager()
        self.recent_files_manager = RecentFilesManager(self.process_file)
        self.file_processor = FileProcessor(self)

        # Load recent files
        self.recent_files_manager.load_recent_files()

        # Setup theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create UI
        self.setup_window()
        self.create_widgets()
        self.setup_layout()
        self.apply_initial_settings()
        self.configure_theme_colors()
        self.create_visualization()

    def configure_theme_colors(self):
        colors = self.theme_manager.get_colors()
        
        # Update customtkinter theme appearance
        ctk.set_appearance_mode(self.theme_manager.current_theme)
        
        # Update styling for legacy widgets (Treeview)
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Custom.Treeview",
            background=colors["secondary"],
            foreground=colors["text"],
            fieldbackground=colors["secondary"],
            borderwidth=0,
            font=("Segoe UI", 11)
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=colors["accent"],
            foreground="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            relief="flat"
        )
        style.map("Custom.Treeview", background=[('selected', colors["accent"])])

    def setup_window(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.scale_var = ctk.DoubleVar(value=1.0)
        ctk.set_widget_scaling(self.scale_var.get())

    def apply_initial_settings(self):
        self.theme_manager.set_theme("dark")
        self.language_manager.set_language("English")
        self.theme_switch.select()
        self.auto_analyze.select()
        self.show_preview.select()

    def create_widgets(self):
        colors = self.theme_manager.get_colors()

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=colors["secondary"])
        
        # Logo section
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_icon = ctk.CTkLabel(
            self.logo_frame,
            text="🛡️",
            font=ctk.CTkFont(size=32),
            text_color=colors["accent"]
        )
        self.logo = ctk.CTkLabel(
            self.logo_frame,
            text="DataSanctum",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=colors["text"]
        )

        # File actions section
        self.file_section = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.file_actions_label = ctk.CTkLabel(
            self.file_section,
            text=self.language_manager.get_text("file_actions"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=colors["text"]
        )
        
        self.btn_open = ctk.CTkButton(
            self.file_section, text=self.language_manager.get_text("open_file"), command=self.open_file_dialog,
            height=45, fg_color=colors["accent"], hover_color="#4F46E5", corner_radius=12,
            font=ctk.CTkFont(family="Segoe UI", weight="bold"), anchor="w", image=self.create_icon_image("📂", 20)
        )
        self.btn_clear = ctk.CTkButton(
            self.file_section, text=self.language_manager.get_text("clear"), command=self.clear_content,
            height=45, fg_color="#EF4444", hover_color="#DC2626", corner_radius=12,
            font=ctk.CTkFont(family="Segoe UI", weight="bold"), anchor="w", image=self.create_icon_image("🗑️", 20)
        )

        # Analyze button
        self.analyze_btn = ctk.CTkButton(
            self.sidebar,
            text=self.language_manager.get_text("analyze_text"),
            command=self.analyze_text_input,
            height=50,
            fg_color="#10B981",
            hover_color="#059669",
            corner_radius=12,
            font=ctk.CTkFont(family="Segoe UI", weight="bold"),
            anchor="w",
            image=self.create_icon_image("🔍", 20)
        )

        # Appearance & Settings
        self.settings_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.create_appearance_controls()

        # Main content
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        
        # Top tools (Drop area + Recent files)
        self.top_tools_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        # Enhanced Drop Area
        self.drop_area = ctk.CTkFrame(self.top_tools_frame, border_width=2, border_color=colors["accent"], corner_radius=20, fg_color=colors["drop_area"])
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.on_drop)
        self.drop_area.dnd_bind('<<DragEnter>>', self.on_drop_area_hover)
        self.drop_area.dnd_bind('<<DragLeave>>', self.on_drop_area_leave)
        
        self.drop_canvas = ctk.CTkCanvas(self.drop_area, highlightthickness=0, bg=colors["drop_area"])
        self.drop_content = ctk.CTkFrame(self.drop_canvas, fg_color="transparent")
        
        # Folder Icon in drop area
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        try:
            folder_image = CTkImage(Image.open(os.path.join(assets_dir, "folder.png")), size=(80, 80))
            self.drop_icon = ctk.CTkLabel(self.drop_content, image=folder_image, text="")
        except:
            self.drop_icon = ctk.CTkLabel(self.drop_content, text="📦", font=ctk.CTkFont(size=60))

        self.drop_label = ctk.CTkLabel(
            self.drop_content, 
            text=self.language_manager.get_text("drag_drop"), 
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=colors["text"]
        )
        self.formats_label = ctk.CTkLabel(
            self.drop_content, 
            text=self.language_manager.get_text("formats"), 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=colors["text"]
        )


        # Recent files section
        self.recent_frame = ctk.CTkFrame(self.top_tools_frame, corner_radius=20, fg_color=colors["secondary"])
        self.recent_header = ctk.CTkFrame(self.recent_frame, fg_color="transparent")
        self.recent_label = ctk.CTkLabel(self.recent_header, text=self.language_manager.get_text("recent_files"), font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"))
        self.btn_clear_history = ctk.CTkButton(
            self.recent_header, text=self.language_manager.get_text("clear_history"), width=40, height=25,
            command=self.clear_recent_files, fg_color="transparent", text_color=colors["text"],
            hover=False, font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.recent_list = ctk.CTkScrollableFrame(self.recent_frame, height=200, fg_color="transparent")

        # Tabs section
        self.content_container = ctk.CTkFrame(self.main_frame, corner_radius=20, fg_color=colors["secondary"])
        self.notebook = TabView(self.content_container, corner_radius=15)
        
        # Content Tab
        self.content_tab = self.notebook.add("📝 " + self.language_manager.get_text("content"))
        self.content_text = ctk.CTkTextbox(self.content_tab, wrap="word", font=ctk.CTkFont(family="Consolas", size=14), border_width=0, corner_radius=10)
        
        # Metadata Tab
        self.metadata_tab = self.notebook.add("📋 " + self.language_manager.get_text("metadata"))
        self.metadata_table = ttk.Treeview(self.metadata_tab, columns=("value"), show="tree", height=10, style="Custom.Treeview")
        
        # Analysis Tab
        self.analysis_tab = self.notebook.add("📊 " + self.language_manager.get_text("analysis"))
        self.analysis_text = ctk.CTkTextbox(self.analysis_tab, wrap="word", font=ctk.CTkFont(family="Segoe UI", size=13), border_width=0, corner_radius=10)

        # Visualization Tab
        self.visual_tab = self.notebook.add("📈 " + self.language_manager.get_text("visualization"))
        self.visual_frame = ctk.CTkFrame(self.visual_tab, fg_color="transparent")
        self.visual_canvas = None

        # Status bar
        self.status_bar = ctk.CTkFrame(self.main_frame, height=35, fg_color="transparent")
        self.status_label = ctk.CTkLabel(self.status_bar, text=self.language_manager.get_text("status_ready"), anchor="w", font=ctk.CTkFont(family="Segoe UI", size=12))
        self.file_label = ctk.CTkLabel(self.status_bar, text="", anchor="e", font=ctk.CTkFont(family="Segoe UI", size=11))

    def create_appearance_controls(self):
        colors = self.theme_manager.get_colors()
        
        self.appearance_label = ctk.CTkLabel(self.sidebar, text=self.language_manager.get_text("appearance"), font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"))
        
        self.theme_switch = ctk.CTkSwitch(
            self.sidebar,
            text=self.language_manager.get_text("dark_mode"),
            command=self.toggle_theme,
            progress_color=colors["accent"]
        )
        
        self.language_option = ctk.CTkOptionMenu(
            self.sidebar,
            values=["English", "Vietnamese"],
            command=self.change_language,
            height=40,
            corner_radius=12,
            fg_color=colors["accent"]
        )
        
        self.ui_scale_slider = ctk.CTkSlider(
            self.sidebar,
            from_=80, to=120,
            number_of_steps=4,
            command=self.change_scaling
        )
        self.ui_scale_slider.set(100)

        self.auto_analyze = ctk.CTkCheckBox(self.sidebar, text=self.language_manager.get_text("auto_analyze"))
        self.show_preview = ctk.CTkCheckBox(self.sidebar, text=self.language_manager.get_text("show_preview"))

    def create_icon_image(self, emoji, size):
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        try:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(image)
            # Use default font if emoji font fails
            draw.text((size//2, size//2), emoji, anchor="mm", font=None)
        except:
            pass
        return ctk.CTkImage(light_image=image, dark_image=image, size=(size, size))

    def setup_layout(self):
        # Sidebar layout
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.logo_frame.pack(pady=(30, 40), padx=20, fill="x")
        self.logo_icon.pack(side="left", padx=(0, 10))
        self.logo.pack(side="left")

        self.file_section.pack(fill="x", padx=20, pady=(0, 20))
        self.file_actions_label.pack(anchor="w", pady=(0, 10))
        self.btn_open.pack(fill="x", pady=(0, 10))
        self.btn_clear.pack(fill="x", pady=(0, 10))

        self.analyze_btn.pack(fill="x", padx=20, pady=(10, 30))

        # Bottom section of sidebar
        self.appearance_label.pack(anchor="w", padx=20, pady=(10, 5))
        self.theme_switch.pack(anchor="w", padx=20, pady=5)
        self.language_option.pack(fill="x", padx=20, pady=10)
        self.auto_analyze.pack(anchor="w", padx=20, pady=2)
        self.show_preview.pack(anchor="w", padx=20, pady=2)
        
        # Main content layout
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.top_tools_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        self.top_tools_frame.grid_columnconfigure(0, weight=3)
        self.top_tools_frame.grid_columnconfigure(1, weight=1)

        self.drop_area.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.drop_canvas.pack(fill="both", expand=True, padx=20, pady=20)
        self.drop_content.pack(expand=True)
        self.drop_icon.pack(pady=(10, 5))
        self.drop_label.pack(pady=5)
        self.formats_label.pack(pady=(0, 10))

        self.recent_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.recent_header.pack(fill="x", padx=15, pady=15)
        self.recent_label.pack(side="left")
        self.btn_clear_history.pack(side="right")
        self.recent_list.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        self.content_container.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        self.content_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.metadata_table.pack(fill="both", expand=True, padx=10, pady=10)
        self.analysis_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.visual_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.status_bar.grid(row=2, column=0, sticky="ew")
        self.status_label.pack(side="left", padx=10)
        self.file_label.pack(side="right", padx=10)

    # Event Handlers
    def on_drop(self, event):
        file_paths = self.tk.splitlist(event.data)
        for path in file_paths:
            path = path.strip('{}')
            if os.path.isfile(path):
                self.process_file(path)
        self.on_drop_area_leave(None)

    def on_drop_area_hover(self, event):
        colors = self.theme_manager.get_colors()
        self.drop_area.configure(border_color="#FFFFFF" if self.theme_manager.current_theme == "dark" else colors["accent"])

    def on_drop_area_leave(self, event):
        colors = self.theme_manager.get_colors()
        self.drop_area.configure(border_color=colors["accent"])

    def process_file(self, file_path):
        try:
            self.file_path = file_path
            self.update_status("processing", os.path.basename(file_path))
            content = self.file_processor.read_file_content(file_path)
            
            if self.show_preview.get():
                self.show_content(content)
            
            self.show_metadata(file_path)
            self.recent_files_manager.add_to_history(file_path)
            self.update_recent_files()
            
            if self.auto_analyze.get():
                self.analyze_text_input()
                
            self.update_status("ready")
        except Exception as e:
            self.update_status("error", str(e))
            messagebox.showerror("Error", f"Could not process file: {str(e)}")

    def show_content(self, content):
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", str(content))
        self.notebook.set("📝 " + self.language_manager.get_text("content"))

    def analyze_text_input(self):
        text = self.content_text.get("1.0", "end-1c")
        if not text.strip():
            return
            
        self.update_status("processing", "Analyzing...")
        stats = self.file_processor.analyze_text(text)
        
        # Match with categories
        try:
            assets_dir = os.path.join(os.path.dirname(__file__), "assets")
            with open(os.path.join(assets_dir, "categories_v2_output.json"), "r", encoding="utf-8") as f:
                categories = json.load(f)
                
            matched = self.file_processor.analyze_content(
                json_data=categories,
                root_dir="./classified_files",
                keyword_embeddings=stats["embeddings"],
                keywords=stats["keywords"],
                input_file_path=self.file_path if hasattr(self, 'file_path') else None
            )
            stats["matched_topic"] = matched
            self.show_analysis(stats)
            self.create_visualization()
            self.update_status("ready")
        except Exception as e:
            self.update_status("error", str(e))

    def show_analysis(self, stats):
        self.analysis_text.delete("1.0", "end")
        
        lines = []
        if "keywords" in stats and stats["keywords"]:
            lines.append("🔑 Keywords:")
            for kw in stats["keywords"]:
                lines.append(f"  • {kw}")
            lines.append("")

        if "matched_topic" in stats and stats["matched_topic"]:
            mt = stats["matched_topic"]
            lines.append("📚 Matched Topic:")
            lines.append(f"  • Topic: {mt.get('topic_name')}")
            lines.append(f"  • Similarity: {mt.get('similarity', 0):.2f}")
            
        self.analysis_text.insert("1.0", "\n".join(lines))
        
        mode = ctk.get_appearance_mode()
        self.analysis_text.configure(text_color="#FFFFFF" if mode == "Dark" else "#333333")
        self.notebook.set("📊 " + self.language_manager.get_text("analysis"))

    def show_metadata(self, file_path):
        self.metadata_table.delete(*self.metadata_table.get_children())
        try:
            stat = os.stat(file_path)
            meta = [
                (self.language_manager.get_text("file_name"), os.path.basename(file_path)),
                (self.language_manager.get_text("file_size"), f"{stat.st_size/1024:.2f} KB"),
                (self.language_manager.get_text("created"), datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M')),
                (self.language_manager.get_text("modified"), datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')),
            ]
            for i, (k, v) in enumerate(meta):
                self.metadata_table.insert("", "end", text=k, values=(v,))
            self.file_label.configure(text=os.path.basename(file_path))
        except Exception as e:
            print(f"Metadata error: {e}")

    def create_visualization(self):
        # Clear previous visualization
        if self.visual_canvas:
            self.visual_canvas.get_tk_widget().destroy()
            plt.close(self.visual_canvas.figure)
            self.visual_canvas = None

        try:
            json_file_path = "./classified_files/node.json"
            if not os.path.exists(json_file_path):
                return

            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data or len(data) < 2:
                # Need at least 2 points for PCA to 2D
                return

            embeddings = np.array([item["embedding"] for item in data])
            keywords = [item["keyword"] for item in data]

            # Reduce dimensions to 2D
            pca = PCA(n_components=2)
            coords = pca.fit_transform(embeddings)

            # Create plot
            mode = ctk.get_appearance_mode()
            bg_color = "#1A1A1A" if mode == "Dark" else "#F3F4F6"
            text_color = "white" if mode == "Dark" else "black"

            fig, ax = plt.subplots(figsize=(6, 4), facecolor=bg_color)
            ax.set_facecolor(bg_color)
            
            # Scatter plot
            scatter = ax.scatter(coords[:, 0], coords[:, 1], c="#4F46E5", s=100, alpha=0.7, edgecolors="white")
            
            # Add labels
            for i, txt in enumerate(keywords):
                ax.annotate(txt, (coords[i, 0], coords[i, 1]), xytext=(5, 5), 
                            textcoords='offset points', color=text_color, fontsize=9)

            # Style axes
            ax.tick_params(colors=text_color)
            for spine in ax.spines.values():
                spine.set_color(text_color)
            
            ax.set_title("File Node Clusters (PCA)", color=text_color, pad=20)

            # Embed in Tkinter
            self.visual_canvas = FigureCanvasTkAgg(fig, master=self.visual_frame)
            self.visual_canvas.draw()
            canvas_widget = self.visual_canvas.get_tk_widget()
            canvas_widget.configure(bg=bg_color)
            canvas_widget.pack(fill="both", expand=True)
            
        except Exception as e:
            print(f"Visualization error: {e}")

    def update_recent_files(self):
        for widget in self.recent_list.winfo_children():
            widget.destroy()
        for path in self.recent_files_manager.recent_files:
            if os.path.exists(path):
                name = os.path.basename(path)
                btn = ctk.CTkButton(
                    self.recent_list, text=f"📄 {name}", 
                    command=lambda p=path: self.process_file(p),
                    anchor="w", height=35, fg_color="transparent", 
                    text_color=self.theme_manager.get_colors()["text"],
                    hover_color=("#E5E7EB", "#374151")
                )
                btn.pack(fill="x", pady=2, padx=5)

    def update_status(self, status, msg=""):
        colors = {"ready": "#10B981", "processing": "#F59E0B", "error": "#EF4444"}
        text = self.language_manager.get_text(f"status_{status}")
        if msg: text += f" ({msg})"
        self.status_label.configure(text=text, text_color=colors.get(status, "#FFFFFF"))

    def toggle_theme(self):
        new_theme = "light" if ctk.get_appearance_mode() == "Dark" else "dark"
        self.theme_manager.set_theme(new_theme)
        self.configure_theme_colors()
        self.update_ui_text()

    def change_language(self, lang):
        self.language_manager.set_language(lang)
        self.update_ui_text()

    def change_scaling(self, value):
        ctk.set_widget_scaling(value/100)

    def update_ui_text(self):
        # Refresh all labels with current language strings
        self.logo.configure(text=self.language_manager.get_text("title"))
        self.btn_open.configure(text=self.language_manager.get_text("open_file"))
        self.btn_clear.configure(text=self.language_manager.get_text("clear"))
        self.analyze_btn.configure(text=self.language_manager.get_text("analyze_text"))
        self.theme_switch.configure(text=self.language_manager.get_text("dark_mode" if ctk.get_appearance_mode() == "Dark" else "light_mode"))
        self.language_option.set("English" if self.language_manager.current_language == "en" else "Vietnamese")
        
        # Update sidebar labels
        self.file_actions_label.configure(text=self.language_manager.get_text("file_actions"))
        self.appearance_label.configure(text=self.language_manager.get_text("appearance"))
        self.auto_analyze.configure(text=self.language_manager.get_text("auto_analyze"))
        self.show_preview.configure(text=self.language_manager.get_text("show_preview"))
        
        # Update main area
        self.drop_label.configure(text=self.language_manager.get_text("drag_drop"))
        self.formats_label.configure(text=self.language_manager.get_text("formats"))
        self.recent_label.configure(text=self.language_manager.get_text("recent_files"))
        self.btn_clear_history.configure(text=self.language_manager.get_text("clear_history"))

        self.update_recent_files()
        self.update_status("ready")

    def open_file_dialog(self):
        path = filedialog.askopenfilename()
        if path: self.process_file(path)

    def clear_content(self):
        self.content_text.delete("1.0", "end")
        self.metadata_table.delete(*self.metadata_table.get_children())
        self.analysis_text.delete("1.0", "end")
        self.file_label.configure(text="")
        if self.visual_canvas:
            self.visual_canvas.get_tk_widget().destroy()
            plt.close(self.visual_canvas.figure)
            self.visual_canvas = None
        self.update_status("ready")

    def clear_recent_files(self):
        self.recent_files_manager.clear()
        self.update_recent_files()

    def on_closing(self):
        if self.visual_canvas:
            plt.close(self.visual_canvas.figure)
        self.destroy()

    def add_analyze_button(self):
        # Dummy to match previous logic if needed, but we already have it in create_widgets
        return None
