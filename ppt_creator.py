import collections
import collections.abc
import os

from pptx import Presentation

class LyricsPptCreator:
    """Class to create lyrics ppt file"""

    NEW_SECTION_TOKEN = '-'
    NUM_OF_LANGUAGES = 4

    def __init__(self) -> None:
        pass

    def create_lyrics_ppt(self) -> str:
        """Method to create lyrics ppt file"""

        ppt = Presentation(os.path.abspath('resource/template/empty_template.pptx'))
        lyrics_layout = ppt.slide_layouts[1]

        lyrics_file_path = os.path.abspath('resource/lyrics/test_lyrics.txt')
        self.__validate_lyrics_file(lyrics_file_path)

        hymn_nums = [0] * 5

        with open(lyrics_file_path, 'r', encoding='UTF-8') as lyrics_file:
            lines = lyrics_file.readlines()

            line_in_title_slide_counter = 0
            line_in_lyric_slide_counter = 0
            title_slide_counter = 0
            slide_counter = 0
            section_counter = 0
            for line in lines:
                # title slide
                if title_slide_counter < 4:
                    hymn_num = line.split(' ', 1)[0].strip()
                    hymn_nums[line_in_title_slide_counter] = hymn_num
                    ppt.slides[0].shapes[line_in_title_slide_counter].text = hymn_num
                    hymn_name = line.split(' ', 1)[1].strip()
                    ppt.slides[0].shapes[line_in_title_slide_counter + 4].text = hymn_name
                    line_in_title_slide_counter += 1
                    title_slide_counter += 1
                    continue

                # lyrics slide
                if self.__is_new_section(line):
                    if section_counter % 2 == 0:
                        slide_counter += 1
                        ppt.slides.add_slide(lyrics_layout)
                        line_in_lyric_slide_counter = 0
                        section_counter = 0

                        line_split_list = line.split(' ', 1)
                        if len(line_split_list) == 2:
                            ppt.slides[slide_counter].shapes[8].text = line_split_list[1].strip()
                            line_in_lyric_slide_counter = 0

                    section_counter += 1
                    continue

                ppt.slides[slide_counter].shapes[line_in_lyric_slide_counter].text = line.strip()
                line_in_lyric_slide_counter += 1

        file_name = f'E{hymn_nums[0]}_K{hymn_nums[1]}_S{hymn_nums[2]}_C{hymn_nums[3]}.pptx'
        file_path = os.path.abspath(f'resource/output/{file_name}')
        ppt.save(file_path)
        print(f'Successfully created a ppt file in path, {file_path}')

        return file_path

    def __validate_lyrics_file(self, lyrics_file_path):
        print(f'Validation of the lyrics file, \"{lyrics_file_path}\", is starting')

        with open(lyrics_file_path, 'r', encoding='UTF-8') as lyrics_file:
            lines = lyrics_file.readlines()
            line_in_section_counter = 0
            for line in lines:
                if self.__is_new_section(line):
                    if line_in_section_counter == self.NUM_OF_LANGUAGES:
                        line_in_section_counter = 0
                        continue
                    else:
                        raise ValueError(
                            f'The number of lines between \"{self.NEW_SECTION_TOKEN}\" \
should always be {self.NUM_OF_LANGUAGES}, \
but it is {line_in_section_counter} in a section')

                line_in_section_counter += 1

        print(f'Validation of the lyrics file, \"{lyrics_file_path}\", is completed successfully')

    def __is_new_section(self, line) -> bool:
        return line.startswith(self.NEW_SECTION_TOKEN)
