"""Module creating the flask app"""
import os
import shutil
import uuid

from flask import Flask, redirect, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename
from ppt_creator import LyricsPptCreator

def create_app():
    """Function creating the flask app"""
    app = Flask(__name__)

    # Initialize Flask extensions here

    # Register blueprints here

    @app.route('/')
    def index():
        return render_template('index.html', title='Hymn PPT Creator')

    @app.route('/save_input/', methods=['POST'])
    def save_input():
        if request.method == 'POST':
            uuid_id = uuid.uuid4()
            os.mkdir(__get_input_file_directory(uuid_id), 0o777)
            input_file = request.files['filename']
            input_file_name = secure_filename(input_file.filename)

            file_ext = os.path.splitext(input_file_name)
            if file_ext != '.txt':
                raise ValueError(f'The file extension has to be .txt, but is {file_ext}')

            input_file_path = __get_input_file_path(uuid_id, input_file_name)
            input_file.save(input_file_path)
            return redirect(url_for('downloads', uuid_id=uuid_id, input_file_name=input_file_name))

    @app.route('/downloads/<uuid_id>/<input_file_name>')
    def downloads(uuid_id, input_file_name):
        lyrics_ppt_creator = LyricsPptCreator()
        input_file_path = __get_input_file_path(uuid_id, input_file_name)
        output_file_path = lyrics_ppt_creator.create_lyrics_ppt(input_file_path)

        print(f'Sending the ouput file, {output_file_path}')
        result = send_file(output_file_path, as_attachment=True)

        __delete_file_and_its_directory(input_file_path)
        __delete_file_and_its_directory(output_file_path)

        return result

    def __get_input_file_directory(uuid_id):
        return os.path.abspath(f'resource/input/{uuid_id}')

    def __get_input_file_path(uuid_id, input_file_name):
        return os.path.join(__get_input_file_directory(uuid_id), input_file_name)

    def __delete_file_and_its_directory(file_path):
        directory_path = os.path.dirname(file_path)
        print(f'Deleting the file, {file_path}, and its directory')
        shutil.rmtree(directory_path)

    return app
