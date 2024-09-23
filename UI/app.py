from flask import Flask, send_from_directory, jsonify, request
import os
import json
import tkinter as tk
from tkinter import filedialog

app = Flask(__name__)
settings_file = 'settings.json'
manga_folder = 'manga'
current_chapter = 0

dark_mode = False  # Default is light mode

def load_settings():
    global manga_folder, current_chapter, dark_mode
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
            manga_folder = settings.get('folder', 'manga')
            current_chapter = settings.get('chapter', 0)
            dark_mode = settings.get('dark_mode', False)  # Load dark mode from settings

def save_settings():
    with open(settings_file, 'w') as f:
        json.dump({
            'folder': manga_folder,
            'chapter': current_chapter,
            'dark_mode': dark_mode  # Save dark mode to settings
        }, f)

@app.route('/save-settings', methods=['POST'])
def save_settings_route():
    data = request.json
    global manga_folder, current_chapter, dark_mode
    manga_folder = data.get('folder', manga_folder) # type: ignore
    current_chapter = data.get('chapter', current_chapter) # type: ignore
    dark_mode = data.get('dark_mode', dark_mode)  # Get dark mode from request # type: ignore
    save_settings()  # Call the save function whenever settings are changed
    return '', 204

@app.route('/load-settings')
def load_settings_route():
    load_settings()
    return jsonify({
        'folder': manga_folder,
        'chapter': current_chapter,
        'dark_mode': dark_mode  # Send dark mode state to frontend
    })

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/chapters')
def chapters():
    files = sorted(os.listdir(manga_folder))
    return jsonify(files)

@app.route('/chapter/<chapter_name>')
def chapter(chapter_name):
    files = sorted(os.listdir(manga_folder))
    for file in files:
        if file == chapter_name:
            return send_from_directory(manga_folder, file)
    return "Chapter not found", 404

@app.route('/choose-folder')
def choose_folder():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    root.destroy()  # Ensure the Tkinter root window is properly destroyed
    if folder_selected:  # Only proceed if a folder is actually selected
        global manga_folder
        manga_folder = folder_selected
        files = sorted(os.listdir(manga_folder))
        save_settings()
        return jsonify({'chapters': files, 'folder': manga_folder})
    else:
        return jsonify({'chapters': [], 'folder': None})  # Return empty if no folder is selected


@app.route('/load-folder')
def load_folder_route():
    folder = request.args.get('folder')
    files = sorted(os.listdir(folder))
    return jsonify(files)

if __name__ == '__main__':
    load_settings()
    app.run(debug=True)
