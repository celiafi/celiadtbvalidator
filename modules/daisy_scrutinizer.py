import re
from modules.external_program_caller import ExternalProgramCaller
from modules.config_getter import ConfigGetter
import pathlib
import os


def extract_metadata(line):
    line = re.sub(r'.+content=(.+") */ *>.*', r'\1', line)
    line = re.sub(r'" *scheme=.+', '', line)
    line = re.sub(r'"', '', line)
    return line


class DaisyScrutinizer:

    @staticmethod
    def get_metadata(ncc, charendcoding):
        prev_generators = []
        metadata = ["dc:title", "dc:creator", "dc:date", "dc:identifier", "dc:language", "dc:publisher", "dc:source",
                    "ncc:narrator", "ncc:producer", "dc:format", "ncc:generator", "ncc:pageNormal", "ncc:pageFront",
                    "ncc:pageSpecial", "ncc:depth", "ncc:charset", "ncc:multimediaType", "ncc:tocItems",
                    "ncc:totalTime", "ncc:files"]
        found_metadata = []

        for s in metadata:
            found_metadata.append("")

        if pathlib.Path.exists(pathlib.Path(ncc)):

            with open(ncc, "r", encoding=charendcoding, errors="replace") as f:
                data = f.read().splitlines()

                for line in data:
                    if re.search(r"prod:prevGenerator", line):
                        prev_generators.append(extract_metadata(line))
                    i = 0
                    while i < len(metadata):
                        if re.search(r"" + metadata[i], line):
                            found_metadata[i] = extract_metadata(line)
                        i += 1

        found_metadata.append(prev_generators)

        return found_metadata

    @staticmethod
    def count_daisy_files(files):
        image_types = ["jpg", "jpeg", "png", "gif", "tiff"]
        smil_count = 0
        audio_files_count = 0
        ncc_count = 0
        master_smil_count = 0
        image_files = 0
        css_files = 0
        other_files_count = 0

        for f in files:
            if f.f_type == "smil" and f.name != "master":
                smil_count += 1
            elif f.f_type == "wav" or f.f_type == "mp3":
                audio_files_count += 1
            elif f.name == "ncc":
                ncc_count += 1
            elif f.name == "master":
                master_smil_count += 1
            elif f.f_type in image_types:
                image_files += 1
            elif f.f_type == "css":
                css_files += 1
            else:
                other_files_count += 1

        return [ncc_count, audio_files_count, smil_count, master_smil_count, image_files, css_files, other_files_count]

    @staticmethod
    def validate_daisy(ncc):
        errors = []
        warnings = []

        pipeline_path = pathlib.Path(ConfigGetter.get_configs("pipeline_path"))
        if not pipeline_path.exists():
            print("Daisy validator not found! Skipping validation!")
            errors.append("Validator not found at location " + str(pipeline_path) + "! CAN NOT VALIDATE DAISY!")
            results = [errors, warnings]
            return results

        cmd_validator = ConfigGetter.get_configs("pipeline_validator_cmd")

        # NOTE! It seems there is a bug in pipeline, so that the pipelinecli can not be run from any other location,
        # than from where it is installed. Trying to run it from any other location causes "Could not
        # find or load main class"-error. As a workaround in this program the location
        # is changed before any pipeline commands. The workaround does following:
        #
        # cmd /c ...                                  # cmd starts in what ever drive it is called from...
        # C:                                          # ...but cmd has to be on drive 'C:'
        # cd pipeline_path                            # ...or "cd pipeline_path" command won't work
        # pipeline commands

        cmd_validate = 'cmd /c "C: & cd ' + str(pipeline_path) + ' & ' + cmd_validator + ' "--input=' + ncc + '"" '
        validator_output = ExternalProgramCaller.run_external_command(cmd_validate).splitlines()

        for line in validator_output:
            # print(line)
            if re.search(r".ERROR, Validator. ", line):
                line = re.sub(r".ERROR, Validator. ", "", line)
                errors.append(line)
            elif re.search(r".WARNING, Validator. ", line):
                line = re.sub(r".WARNING, Validator. ", "", line)
                warnings.append(line)

        results = [errors, warnings]
        return results

    @staticmethod
    def check_first_smil(files):
        audio_references = 0
        smils = []
        for f in files:
            if f.f_type == "smil" and f.name != "master":
                smils.append(f.path)

        smils.sort()

        if len(smils) > 0:
            first_smil = smils[0]
            data = open(first_smil, "r", errors="replace").read().splitlines()

            for line in data:
                if re.search(r"audio src=", line):
                    audio_references += 1

        return audio_references

    @staticmethod
    def find_pagemark_errors(files):
        smils = []
        for f in files:
            if f.f_type == "smil" and f.name != "master":
                smils.append(f.path)

        page_mark_errors = []

        if len(smils) > 0:
            for smil in smils:
                line_a = ""
                line_b = ""
                line_c = ""
                data = open(smil, "r", errors="replace").read().splitlines()

                heading_title = ""

                for line in data:
                    if re.search(r'meta name="title"', line):
                        heading_title = extract_metadata(line)
                    line_c = line_b
                    line_b = line_a
                    line_a = line

                    if re.search(r".+<par.+\">", line_c) and re.search(r".+text", line_b) and re.search(r".+</par>",
                                                                                                        line_a):
                        page_mark_errors.append([heading_title, smil])

        return page_mark_errors

    @staticmethod
    def encode_audio(ncc, output_path):
        # pipeline-cli.bat scripts\modify_improve\dtb\DTBAudioEncoder.taskScript "--input=path\ncc.html"
        # "--output=outpath" "--bitrate=48"
        pipeline_path = pathlib.Path(ConfigGetter.get_configs("pipeline_path"))
        if pipeline_path.exists():
            cmd_encode = ConfigGetter.get_configs("pipeline_audioencoder_cmd")

            target_kbps = ConfigGetter.get_configs("target_kbps")
            if not target_kbps == "32" or not target_kbps == "48" or not target_kbps == "64" or not target_kbps == "128":
                target_kbps = "48"

            cmd_encode_audio = 'C: & cd ' + str(pipeline_path) + ' & ' + cmd_encode \
                               + ' "--input=' + ncc + '" "--output=' + output_path + '"  "--bitrate=' + target_kbps + '"'
            os.system(cmd_encode_audio)

            print("Validating encoded Daisy book...")

            output_ncc = pathlib.Path.joinpath(pathlib.Path(output_path), "ncc.html")
            validator_checks = DaisyScrutinizer.validate_daisy(str(output_ncc))

            if len(validator_checks[0]) == 0 and len(validator_checks[1]) == 0:
                print("No errors or warning reported.")
            else:
                for err in validator_checks[0]:
                    print(err)
                for warn in validator_checks[1]:
                    print(warn)

        else:
            print("Daisy pipeline not found! Skipping audio encoding!")
