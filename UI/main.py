from core.app import FileAnalyzerApp


if __name__ == "__main__":
    app = FileAnalyzerApp()
    app.add_analyze_button()  
    app.mainloop()