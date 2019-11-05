from modules.daisy_scrutinizer import DaisyScrutinizer
from modules.file_scrutinizer import FileScrutinizer
from modules.generic_file import GenericFile
from modules.audio_file import AudioFile
from modules.config_getter import ConfigGetter
import sys


class AudioBook:

    def __init__(self, path):
        self.path = path
        self.kbps = 0.0
        self.lufs = 0.0
        self.pkdb = 0.0
        self.tpkdb = 0.0
        self.snr = 0.0
        self.files = []
        self.filename_prefix = ""
        self.daisy_validation_errors = []
        self.daisy_validation_warnings = []

        skip_daisy_checks = False
        if not ConfigGetter.get_configs("daisy_validation") == "1":
            skip_daisy_checks = True

        skip_audio_checks = False
        if not ConfigGetter.get_configs("audio_validation") == "1":
            skip_audio_checks = True

        if skip_audio_checks and skip_daisy_checks:
            input("Confuration set to skip daisy AND audio checks! Nothing to do...")
            sys.exit()

        print("Processing files...")

        files_in_folder = FileScrutinizer.list_files_in_folder(self.path)
        i = 0
        for f in files_in_folder:
            i += 1
            f_info = FileScrutinizer.find_fname_ftype(f)
            print("Processing file " + f_info[0] + "." + f_info[1] + " (" + str(i) + "/" + str(len(files_in_folder)) + ")")
            if (f_info[1].lower() == "wav" or f_info[1].lower() == "mp3") and not skip_audio_checks:
                new_file = AudioFile(f, f_info[0], f_info[1])
            else:
                new_file = GenericFile(f, f_info[0], f_info[1])
            self.files.append(new_file)

        self.ncc_count = 0
        self.audio_file_count = 0
        self.smil_count = 0
        self.master_smil_count = 0
        self.image_count = 0
        self.css_count = 0
        self.other_filetype_count = 0
        self.pagemark_errors = []

        file_count = DaisyScrutinizer.count_daisy_files(self.files)
        self.ncc_count = file_count[0]
        self.audio_file_count = file_count[1]
        self.smil_count = file_count[2]
        self.master_smil_count = file_count[3]
        self.image_count = file_count[4]
        self.css_count = file_count[5]
        self.other_filetype_count = file_count[6]

        if not skip_audio_checks:
            for f in self.files:
                if isinstance(f, AudioFile):
                    self.lufs += f.lufs
                    self.pkdb += f.pkdb
                    self.tpkdb += f.tpkdb
                    self.snr += f.snr
                    self.kbps += f.kbps

            self.lufs = self.lufs / self.audio_file_count
            self.pkdb = self.pkdb / self.audio_file_count
            self.tpkdb = self.tpkdb / self.audio_file_count
            self.snr = self.snr / self.audio_file_count
            self.kbps = self.kbps / self.audio_file_count

        # Daisy Checks...
        if not skip_daisy_checks:
            print("Processing book metadata...")

            charencoding = FileScrutinizer.get_encoding_tag(self.path + "/ncc.html")
            metadata_list = DaisyScrutinizer.get_metadata(self.path + "/ncc.html", charencoding)

            self.dc_title = metadata_list[0]
            self.dc_creator = metadata_list[1]
            self.dc_date = metadata_list[2]
            self.dc_identifier = metadata_list[3]
            self.dc_language = metadata_list[4]
            self.dc_publisher = metadata_list[5]
            self.dc_source = metadata_list[6]
            self.ncc_narrator = metadata_list[7]
            self.ncc_producer = metadata_list[8]
            self.dc_format = metadata_list[9]
            self.ncc_generator = metadata_list[10]
            self.ncc_page_normal = metadata_list[11]
            self.ncc_page_front = metadata_list[12]
            self.ncc_page_special = metadata_list[13]
            self.ncc_depth = metadata_list[14]
            self.ncc_charset = metadata_list[15]
            self.ncc_multimedia_type = metadata_list[16]
            self.ncc_toc_items = metadata_list[17]
            self.ncc_total_time = metadata_list[18]
            self.ncc_files = metadata_list[19]
            self.prod_prev_generator = ""

            for prev_gen in metadata_list[20]:
                if self.prod_prev_generator == "":
                    self.prod_prev_generator = prev_gen
                else:
                    self.prod_prev_generator = self.prod_prev_generator + ", " + prev_gen

            self.filename_prefix = FileScrutinizer.get_filename_prefix(self.files)

            self.pagemark_errors = []

            self.pagemark_errors = DaisyScrutinizer.find_pagemark_errors(self.files)

            self.first_smil_audio_references = DaisyScrutinizer.check_first_smil(self.files)

            print("Running daisy validator...")
            daisy_validation = DaisyScrutinizer.validate_daisy(self.path + "/ncc.html")
            self.daisy_validation_errors = daisy_validation[0]
            self.daisy_validation_warnings = daisy_validation[1]

        else:
            print("Skipping Daisy checks.")
            self.dc_title = ""
            self.dc_creator = ""
            self.dc_date = ""
            self.dc_identifier = ""
            self.dc_language = ""
            self.dc_publisher = ""
            self.dc_source = ""
            self.ncc_narrator = ""
            self.ncc_producer = ""
            self.dc_format = ""
            self.ncc_generator = ""
            self.ncc_page_normal = ""
            self.ncc_page_front = ""
            self.ncc_page_special = ""
            self.ncc_depth = ""
            self.ncc_charset = ""
            self.ncc_multimedia_type = ""
            self.ncc_toc_items = ""
            self.ncc_total_time = ""
            self.ncc_files = ""
            self.prod_prev_generator = ""

            self.filename_prefix = FileScrutinizer.get_filename_prefix(self.files)

            self.pagemark_errors = []

            self.first_smil_audio_references = 0

            self.daisy_validation_errors = []
            self.daisy_validation_warnings = []

