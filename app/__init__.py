"""Module creating the flask app"""
import io
import os
import shutil
import uuid
import zipfile

from datetime import datetime
from flask import Flask, redirect, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename
from app.businesslogic.wed_sermon_ppt_creator import WedSermonLyricsPptCreator
from app.businesslogic.west_coast_ppt_creator import WestCoastLyricsPptCreator
from app.businesslogic.txt_creator import LyricsTxtCreator

def create_app():
    """Function creating the flask app"""
    app = Flask(__name__)

    # Initialize Flask extensions here

    # Register blueprints here

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/to_pptx/')
    def to_pptx():
        return render_template('index.html')

    @app.route('/to_txt/')
    def to_txt():
        return render_template('index.html')

    @app.route('/how_to_use_west_coast_theme/')
    def how_to_use_west_coast_theme():
        return render_template('index.html')

    @app.route('/how_to_use_wed_sermon/')
    def how_to_use_wed_sermon():
        return render_template('index.html')

    # Main method getting called from index.html
    @app.route('/hymn_ppt/', methods=['POST'])
    def generate_hymn_ppt():
        working_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        input_file_directory = os.path.join(working_dir, 'app/static/lyrics')
        uuid_id = uuid.uuid4()
        output_file_directory = __get_output_file_directory(uuid_id)
        use_case = request.form.get('use_case')

        for input_file_name in request.form.getlist('hymn_file_title'):
            input_file_path = os.path.join(input_file_directory, input_file_name)
            try:
                print(f'Creating lyrics ppt file for hymn: {input_file_name} and input: {input_file_path}')
                if 'WedSermon' == use_case: # todo: delete this use case
                    WedSermonLyricsPptCreator().create_lyrics_ppt(input_file_path, uuid_id)
                else: # defaults to west coast theme
                    WestCoastLyricsPptCreator().create_lyrics_ppt(input_file_path, uuid_id)
            except ValueError:
                pass

        if len(request.form.getlist('hymn_file_title')) == 1:
            output_file_path = __get_output_file_path(uuid_id, os.listdir(output_file_directory)[0])
            try:
                print(f'Returning the output file at path: {output_file_path}')
                return send_file(output_file_path, as_attachment=True)
            finally:
                __delete_directory(output_file_directory)

        print(f'Zipping the output files in directory: {output_file_directory}')
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zip_file:
            for output_file in os.listdir(output_file_directory):
                print(f'Zipping the output file: {output_file}')
                output_file_path = __get_output_file_path(uuid_id, output_file)
                zip_file.write(output_file_path, os.path.basename(output_file_path))
        memory_file.seek(0)

        __delete_directory(output_file_directory)

        now_str = datetime.today().strftime('%Y-%m-%d')
        zip_file_name = f'{now_str}-hymn_pptx.zip'
        print(f'Returning the zip file, {zip_file_name}')

        return send_file(memory_file, download_name=zip_file_name, as_attachment=True)

    # Main method getting called from to_pptx.html
    @app.route('/text_files/', methods=['POST'])
    def submit_text_files():
        if request.method != 'POST':
            return

        uuid_id = uuid.uuid4()
        correct_file_ext = '.txt'

        try:
            __save_input_files(request.files.getlist("filename[]"), uuid_id, correct_file_ext)
        except ValueError:
            return redirect(url_for('input_file_type_error', correct_file_ext=correct_file_ext))

        return redirect(url_for('generate_pptx_files', use_case=request.form['use_case'], uuid_id=uuid_id))

    @app.route('/pptx_files/<uuid_id>/<use_case>')
    def generate_pptx_files(uuid_id, use_case):
        input_file_directory = __get_input_file_directory(uuid_id)

        num_of_input_file = 0
        for input_file_name in os.listdir(input_file_directory):
            num_of_input_file += 1
            input_file_path = os.path.join(input_file_directory, input_file_name)
            try:
                print(f'Creating lyrics ppt file for use case: {use_case} and input: {input_file_path}')
                if 'WedSermon' == use_case:
                    WedSermonLyricsPptCreator().create_lyrics_ppt(input_file_path, uuid_id)
                else: # defaults to west coast theme
                    WestCoastLyricsPptCreator().create_lyrics_ppt(input_file_path, uuid_id)
            except ValueError:
                pass

        if num_of_input_file == 1:
            input_file_path = __get_input_file_path(uuid_id, os.listdir(input_file_directory)[0])
            output_file_path = ''
            try:
                print(f'Creating lyrics ppt file for use case: {use_case} and input: {input_file_path}')
                output_file_path = ""
                if 'WedSermon' == use_case:
                    output_file_path = WedSermonLyricsPptCreator().create_lyrics_ppt(input_file_path, uuid_id)
                else: # defaults to west coast theme
                    output_file_path = WestCoastLyricsPptCreator().create_lyrics_ppt(input_file_path, uuid_id)

                print(f'Sending the ouput file, {output_file_path}')
                result = send_file(output_file_path, as_attachment=True)
            except ValueError as error:
                return redirect(url_for('input_file_error', error_msg=str(error)))
            finally:
                __delete_file_and_its_directory(input_file_path)
                __delete_file_and_its_directory(output_file_path)

            return result

        output_file_directory = __get_output_file_directory(uuid_id)
        print(f'Zipping the output files in directory: {output_file_directory}')
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zip_file:
            for output_file in os.listdir(output_file_directory):
                print(f'Zipping the output file: {output_file}')
                output_file_path = __get_output_file_path(uuid_id, output_file)
                zip_file.write(output_file_path, os.path.basename(output_file_path))
        memory_file.seek(0)

        __delete_directory(input_file_directory)
        __delete_directory(output_file_directory)

        now_str = datetime.today().strftime('%Y-%m-%d')
        zip_file_name = f'{now_str}-hymn_pptx.zip'
        print(f'Returning the zip file, {zip_file_name}')

        return send_file(memory_file, download_name=zip_file_name, as_attachment=True)

    # Main method getting called from to_txt.html
    @app.route('/pptx_files/', methods=['POST'])
    def submit_pptx_files():
        if request.method != 'POST':
            return

        uuid_id = uuid.uuid4()
        correct_file_ext = '.pptx'

        try:
            __save_input_files(request.files.getlist("filename[]"), uuid_id, correct_file_ext)
        except ValueError:
            return redirect(url_for('input_file_type_error', correct_file_ext=correct_file_ext))

        return redirect(url_for('generate_text_files', uuid_id=uuid_id))

    @app.route('/text_files/<uuid_id>')
    def generate_text_files(uuid_id):
        lyrics_txt_creator = LyricsTxtCreator()
        input_file_directory = __get_input_file_directory(uuid_id)

        num_of_input_file = 0
        for input_file_name in os.listdir(input_file_directory):
            num_of_input_file += 1
            input_file_path = os.path.join(input_file_directory, input_file_name)
            try:
                print(f'Creating lyrics ppt file for: {input_file_path}')
                lyrics_txt_creator.create_lyrics_txt(input_file_path, uuid_id)
            except ValueError:
                pass

        if num_of_input_file == 1:
            input_file_path = __get_input_file_path(uuid_id, os.listdir(input_file_directory)[0])
            output_file_path = ''
            try:
                output_file_path = lyrics_txt_creator.create_lyrics_txt(input_file_path, uuid_id)

                print(f'Sending the ouput file, {output_file_path}')
                result = send_file(output_file_path, as_attachment=True)
            except ValueError as error:
                return redirect(url_for('input_file_error', error_msg=str(error)))
            finally:
                __delete_file_and_its_directory(input_file_path)
                __delete_file_and_its_directory(output_file_path)

            return result

        output_file_directory = __get_output_file_directory(uuid_id)
        print(f'Zipping the output files in directory: {output_file_directory}')
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zip_file:
            for output_file in os.listdir(output_file_directory):
                print(f'Zipping the output file: {output_file}')
                output_file_path = __get_output_file_path(uuid_id, output_file)
                zip_file.write(output_file_path, os.path.basename(output_file_path))
        memory_file.seek(0)

        __delete_directory(input_file_directory)
        __delete_directory(output_file_directory)

        now_str = datetime.today().strftime('%Y-%m-%d')
        zip_file_name = f'{now_str}-hymn_txt.zip'
        print(f'Returning the zip file, {zip_file_name}')

        return send_file(memory_file, download_name=zip_file_name, as_attachment=True)

    @app.route('/input_file_type_error/<correct_file_ext>')
    def input_file_type_error(correct_file_ext):
        error_message = f'The file extension has to be {correct_file_ext}, but it is not'
        return render_template('error.html', error_type='Invalid Input File Type Error', error_message=error_message)

    @app.route('/input_file_error/<error_msg>')
    def input_file_error(error_msg):
        return render_template('error.html', error_type='Invalid Input File Error', error_message=error_msg)

    def __save_input_files(input_files, uuid_id, correct_file_ext):
        input_file_directory = __get_input_file_directory(uuid_id)
        print(f'input_file_dir: {input_file_directory}')
        os.mkdir(input_file_directory, 0o777)
        for input_file in input_files:
            input_file_name = secure_filename(input_file.filename)
            input_file_path = __get_input_file_path(uuid_id, input_file_name)

            _, file_ext = os.path.splitext(input_file_name)
            if file_ext != correct_file_ext:
                __delete_file_and_its_directory(input_file_path)
                raise ValueError()

            input_file.save(input_file_path)
        return input_file_directory

    def __get_input_file_directory(uuid_id):
        working_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(working_dir, f'resource/input/{uuid_id}')

    def __get_input_file_path(uuid_id, input_file_name):
        return os.path.join(__get_input_file_directory(uuid_id), input_file_name)

    def __get_output_file_directory(uuid_id):
        working_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(working_dir, f'resource/output/{uuid_id}')

    def __get_output_file_path(uuid_id, output_file_name):
        return os.path.join(__get_output_file_directory(uuid_id), output_file_name)

    def __delete_directory(directory_path):
        try:
            print(f'Deleting the directory, {directory_path}')
            shutil.rmtree(directory_path, ignore_errors=True)
        except: # pylint: disable=bare-except
            pass

    def __delete_file_and_its_directory(file_path):
        try:
            directory_path = os.path.dirname(file_path)
            print(f'Deleting the file, {file_path}, and its directory')
            shutil.rmtree(directory_path, ignore_errors=True)
        except: # pylint: disable=bare-except
            pass

    return app
