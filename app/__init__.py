"""Module creating the flask app"""
import os
import shutil
import uuid

from flask import Flask, redirect, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename
from app.businesslogic.ppt_creator import LyricsPptCreator
from app.businesslogic.txt_creator import LyricsTxtCreator

def create_app():
    """Function creating the flask app"""
    app = Flask(__name__)

    # Initialize Flask extensions here

    # Register blueprints here

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/text_file/', methods=['POST'])
    def submit_text_file():
        if request.method == 'POST':
            uuid_id = uuid.uuid4()
            correct_file_ext = '.txt'
            try:
                input_file_name = __save_input_file(request.files['filename'], uuid_id, correct_file_ext)
            except ValueError as error:
                return redirect(url_for('input_file_type_error', correct_file_ext=correct_file_ext))

            return redirect(url_for('generate_pptx_file', uuid_id=uuid_id, input_file_name=input_file_name))

    @app.route('/pptx_file/<uuid_id>/<input_file_name>')
    def generate_pptx_file(uuid_id, input_file_name):
        lyrics_ppt_creator = LyricsPptCreator()
        input_file_path = __get_input_file_path(uuid_id, input_file_name)
        output_file_path = ''
        try:
            output_file_path = lyrics_ppt_creator.create_lyrics_ppt(input_file_path)

            print(f'Sending the ouput file, {output_file_path}')
            result = send_file(output_file_path, as_attachment=True)
        except ValueError as error:
            return redirect(url_for('input_file_error', error_msg=str(error)))
        finally:
            __delete_file_and_its_directory(input_file_path)
            __delete_file_and_its_directory(output_file_path)

        return result

    @app.route('/pptx_file/', methods=['POST'])
    def submit_pptx_file():
        if request.method == 'POST':
            uuid_id = uuid.uuid4()
            correct_file_ext = '.pptx'
            try:
                input_file_name = __save_input_file(request.files['filename'], uuid_id, correct_file_ext)
            except ValueError as error:
                return redirect(url_for('input_file_type_error', correct_file_ext=correct_file_ext))

            return redirect(url_for('generate_text_file', uuid_id=uuid_id, input_file_name=input_file_name))

    @app.route('/text_file/<uuid_id>/<input_file_name>')
    def generate_text_file(uuid_id, input_file_name):
        lyrics_txt_creator = LyricsTxtCreator()
        input_file_path = __get_input_file_path(uuid_id, input_file_name)
        output_file_path = ''
        try:
            output_file_path = lyrics_txt_creator.create_lyrics_txt(input_file_path)

            print(f'Sending the ouput file, {output_file_path}')
            result = send_file(output_file_path, as_attachment=True)
        except ValueError as error:
            return redirect(url_for('input_file_error', error_msg=str(error)))
        finally:
            __delete_file_and_its_directory(input_file_path)
            __delete_file_and_its_directory(output_file_path)

        return result

    @app.route('/input_file_type_error/<correct_file_ext>')
    def input_file_type_error(correct_file_ext):
        error_message = f'The file extension has to be {correct_file_ext}, but it is not'
        return render_template('error.html', error_type='Invalid Input File Type Error', error_message=error_message)

    @app.route('/input_file_error/<error_msg>')
    def input_file_error(error_msg):
        return render_template('error.html', error_type='Invalid Input File Error', error_message=error_msg)
    
    def __save_input_file(input_file, uuid_id, correct_file_ext):
        os.mkdir(__get_input_file_directory(uuid_id), 0o777)
        input_file_name = secure_filename(input_file.filename)
        input_file_path = __get_input_file_path(uuid_id, input_file_name)

        _, file_ext = os.path.splitext(input_file_name)
        if file_ext != correct_file_ext:
            __delete_file_and_its_directory(input_file_path)
            raise ValueError()

        input_file.save(input_file_path)
        return input_file_name

    def __get_input_file_directory(uuid_id):
        working_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(working_dir, f'resource/input/{uuid_id}')

    def __get_input_file_path(uuid_id, input_file_name):
        return os.path.join(__get_input_file_directory(uuid_id), input_file_name)

    def __delete_file_and_its_directory(file_path):
        try:
            directory_path = os.path.dirname(file_path)
            print(f'Deleting the file, {file_path}, and its directory')
            shutil.rmtree(directory_path, ignore_errors=True)
        except: # pylint: disable=bare-except
            pass

    return app
