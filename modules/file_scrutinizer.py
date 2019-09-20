import os
import re
import pathlib


class FileScrutinizer:

    @staticmethod
    def list_files_in_folder(path):
        files_in_folder = []
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = dirpath + "/" + f
                files_in_folder.append(fp)

        return files_in_folder

    @staticmethod
    def count_files(files):
        pass

    @staticmethod
    def get_encoding_tag(ncc):
        found = False
        if pathlib.Path.exists(pathlib.Path(ncc)):
            with open(ncc, "r", encoding="utf-8", errors="replace") as f:
                data = f.read().splitlines()

                for line in data:
                    if re.search(r".+ncc:charset.+", line):
                        if re.search(r"utf-8", line.lower()):
                            f.close()
                            return "utf-8"
                        else:
                            f.close()
                            return "iso-8859-1"
        else:
            return ""

    @staticmethod
    def get_file_prefix(files):
        pass

    @staticmethod
    def find_fname_ftype(path):
        # path --> abc/def/ghi.jk
        path = path.split("/")
        f = path[(len(path) - 1)]
        f = f.split(".")
        return f

    @staticmethod
    def get_filename_prefix(files):
        smil_prefix = ""
        audiofile_prefix = ""
        for file in files:
            f = file.name + "." + file.f_type
            if f.endswith(".wav") or f.endswith(".mp3"):
                tmp = re.sub(r"(.+)_.+.wav", r"\1", f)
                tmp = re.sub(r"(.+)_.+.mp3", r"\1", tmp)
                if tmp == audiofile_prefix:
                    continue
                elif audiofile_prefix != "" and audiofile_prefix != tmp:
                    audiofile_prefix = audiofile_prefix + " / " + tmp
                else:
                    audiofile_prefix = tmp
            elif f.endswith(".smil") and f.lower() != "master.smil":
                tmp = re.sub(r"(.+)_.+.smil", r"\1", f)
                if tmp == smil_prefix:
                    continue
                elif smil_prefix != "" and smil_prefix != tmp:
                    smil_prefix = smil_prefix + " / " + tmp
                else:
                    smil_prefix = tmp
        if smil_prefix == audiofile_prefix:
            return audiofile_prefix
        else:
            return "NO PREFIX FOUND!"
