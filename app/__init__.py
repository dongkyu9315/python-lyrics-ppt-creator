from flask import Flask, render_template, send_file
from ppt_creator import LyricsPptCreator

import os

def create_app():
    app = Flask(__name__)

    # Initialize Flask extensions here

    # Register blueprints here

    @app.route('/')
    def index():
        return render_template('index.html', title='Hymn PPT Creator')

    @app.route('/downloads/')
    def downloads_page():
        lyricsPptCreator = LyricsPptCreator()
        file_path = lyricsPptCreator.create_lyrics_ppt()

        print(f'Sending the file at {file_path}')
        result = send_file(file_path, as_attachment=True)

        print(f'File is sent, deleting the file at {file_path}')
        os.remove(file_path)

        return result

    return app