from modules.audio_book import AudioBook
from modules.audio_file import AudioFile
from modules.config_getter import ConfigGetter
from modules.audio_scrutinizer import AudioScrutinizer
from shutil import which
import pathlib
import sys
import datetime
import webbrowser
import re
from modules.report_generator import ReportGenerator
from modules.daisy_scrutinizer import DaisyScrutinizer


def get_version_num():
    return "v. 0.9.2.2."


def get_args(args):
    # print(args)
    valid_arguments = []
    b_path = ""
    o_path = ""
    r_path = ""
    valid_cmd_handles = ["-i", "-o", "-r", "-h", "-v"]
    if len(args) > 8:
        print("Argument error! Too many arguments!")
        print_manual()
        sys.exit()
    else:
        for a in args:
            if re.search(r"^-", a) and a not in valid_cmd_handles:
                print("Argument error! Unknown argument '" + a + "'")
                print_manual()
                sys.exit()

    index = 0
    while index < len(args):
        if args[index].lower() == "-h":
            print_manual()
            sys.exit()
        elif args[index].lower() == "-v":
            print(get_version_num())
            sys.exit()
        elif args[index].lower() == "-i" and len(args) > index + 1:
            b_path = pathlib.Path(args[index + 1]).absolute()
            # b_path = pathlib.Path(re.sub(r'"', '', args[index + 1])).absolute()
            if not b_path.exists():
                print("Argument error! Defined book path does not exist!")
                print_manual()
                sys.exit()
        elif args[index].lower() == "-o" and len(args) > index + 1:
            o_path = pathlib.Path(args[index + 1]).absolute()
            if not o_path.exists():
                print("Argument error! Defined output path does not exist!")
                print_manual()
                sys.exit()
        elif args[index].lower() == "-r" and len(args) > index + 1:
            r_path = pathlib.Path(args[index + 1]).absolute()
            if not r_path.exists():
                print("Argument error! Defined report path does not exist!")
                print_manual()
                sys.exit()
        index += 1

    if b_path == "":
        print("Argument error! No book path defined!")
        print_manual()
        sys.exit()

    valid_arguments = b_path, o_path, r_path
    return valid_arguments


def print_manual():
    print("---------------------------------")
    print("Manual for Celia DTB Validator " + get_version_num())
    print("")
    print("Usage: python celia_dtb_validator.py -i BOOKPATH [-o OUTPUTPATH] [-r REPORTPATH]")
    print("")
    print("Print version number: python celia_dtb_validator.py -v")
    print("Print this manual: python celia_dtb_validator.py -h")
    print("")
    print("NOTE ON PATHS WITH SPACES: ")
    print("If you use paths with spaces you should leave out the last backslash.")
    print("The last backslash will be interpreted as escape character.")
    print("Use 'C:\\Temp\\Path With Spaces' instead of 'C:\\Temp\\Path With Spaces\\'")
    print("You can also use double quotes ie. """'C:\\Temp\\Path With Spaces\\'",")
    print("or use forward slahes instead, ie. 'C:/Temp/Path With Spaces/'")
    print("\n")


class CeliaDTBValidator:

    @staticmethod
    def extract_audio_files(files):
        audio_files = []
        for audio_f in files:
            if isinstance(audio_f, AudioFile):
                audio_files.append(audio_f)
        return audio_files

    @staticmethod
    def validate_dtb(audiobook, output_location, report_location):
        skip_daisy_checks = False
        if not ConfigGetter.get_configs("daisy_validation") == "1":
            skip_daisy_checks = True

        target_text_encoding = ConfigGetter.get_configs("target_text_encoding")
        if target_text_encoding == "":
            target_text_encoding = "utf-8"
        try:
            target_kbps = int(ConfigGetter.get_configs("target_kbps"))
        except:
            target_kbps = 48
        try:
            lufs_min = int(ConfigGetter.get_configs("lufs_min"))
        except:
            lufs_min = -20
        try:
            lufs_max = int(ConfigGetter.get_configs("lufs_max"))
        except:
            lufs_max = -17
        try:
            pkdb_min = int(ConfigGetter.get_configs("pkdb_min"))
        except:
            pkdb_min = -2
        try:
            pkdb_max = int(ConfigGetter.get_configs("pkdb_max"))
        except:
            pkdb_max = 0
        try:
            tpkdb_min = int(ConfigGetter.get_configs("tpkdb_min"))
        except:
            tpkdb_min = -2
        try:
            tpkdb_max = int(ConfigGetter.get_configs("tpkdb_max"))
        except:
            tpkdb_max = 0
        try:
            snr_min = int(ConfigGetter.get_configs("snr_min"))
        except:
            snr_min = 45
        try:
            kbps_min = int(ConfigGetter.get_configs("kbps_min"))
        except:
            kbps_min = 32
        try:
            kbps_max = int(ConfigGetter.get_configs("kbps_max"))
        except:
            kbps_max = 48

        time_stamp = datetime.datetime.today().strftime('%Y-%m-%d-%H%M%S')
        report_out_path = pathlib.Path.joinpath(pathlib.Path(report_location), "dtb_validation_report_"
                                                + time_stamp + "_" + audiobook.dc_identifier + ".html")
        print("Checking dtb...")
        critical_errors = []
        errors = []
        warnings = []

        # Audio only...
        if audiobook.audio_file_count == 0:
            critical_errors.append("No audio-files found!")

        low_lufs = []
        high_lufs = []
        low_pkdb = []
        high_pkdb = []
        low_tpkdb = []
        high_tpkdb = []
        low_snr = []

        audio_files = CeliaDTBValidator.extract_audio_files(audiobook.files)

        for audio_f in audio_files:
            if audio_f.lufs < float(lufs_min):
                low_lufs.append(audio_f.name + "." + audio_f.f_type + " (" + str(audio_f.lufs) + " LUFS)")
            elif audio_f.lufs > float(lufs_max):
                high_lufs.append(audio_f.name + "." + audio_f.f_type + " (" + str(audio_f.lufs) + " LUFS)")
            if audio_f.pkdb < float(pkdb_min):
                low_pkdb.append(audio_f.name + "." + audio_f.f_type + " (" + str(audio_f.pkdb) + " dB)")
            elif audio_f.pkdb > float(pkdb_max):
                high_pkdb.append(audio_f.name + "." + audio_f.f_type + " (" + str(audio_f.pkdb) + " dB)")
            if audio_f.tpkdb < float(tpkdb_min):
                low_tpkdb.append(audio_f.name + "." + audio_f.f_type + " (" + str(audio_f.tpkdb) + " dB)")
            elif audio_f.tpkdb > float(tpkdb_max):
                high_tpkdb.append(audio_f.name + "." + audio_f.f_type + " (" + str(audio_f.tpkdb) + " dB)")
            if audio_f.snr < float(snr_min):
                low_snr.append(audio_f.name + "." + audio_f.f_type + " (" + str(audio_f.snr) + " dB)")

            if not audio_f.end_silence:
                errors.append("File " + audio_f.name + "." + audio_f.f_type + " has no silence at end!")
            if not audio_f.no_start_silence:
                errors.append("No sound at beginning of file " + audio_f.name + "." + audio_f.f_type + "!")
            if not audio_f.no_unexpected_end_silence:
                errors.append(
                    "Unexpectedly long silence found at end of file " + audio_f.name + "." + audio_f.f_type + "!")
            if len(audio_f.mid_silences) > 0:
                errors.append("Unexpected silence found from file " + audio_f.name + "." + audio_f.f_type + "!")
                for mid_silence_err in audio_f.mid_silences:
                    errors.append("    " + mid_silence_err)

        if len(low_lufs) > 0:
            errors.append("LUFS values too low on " + str(len(low_lufs)) + " files:")
            for lufs_e in low_lufs:
                errors.append("    " + lufs_e)
        if len(high_lufs) > 0:
            errors.append("LUFS values too high on " + str(len(high_lufs)) + " files:")
            for lufs_e in high_lufs:
                errors.append("    " + lufs_e)

        if len(low_pkdb) > 0:
            errors.append("pkdb values too low on " + str(len(low_pkdb)) + " files:")
            for pkdb_e in low_pkdb:
                errors.append("    " + pkdb_e)
        if len(high_pkdb) > 0:
            errors.append("pkdb values too high on " + str(len(high_pkdb)) + " files:")
            for pkdb_e in high_pkdb:
                errors.append("    " + pkdb_e)

        if len(low_tpkdb) > 0:
            errors.append("tpkdb values too low on " + str(len(low_tpkdb)) + " files:")
            for tpkdb_e in low_tpkdb:
                errors.append("    " + tpkdb_e)
        if len(high_tpkdb) > 0:
            errors.append("tpkdb values too high on " + str(len(high_tpkdb)) + " files:")
            for tpkdb_e in high_tpkdb:
                errors.append("    " + tpkdb_e)

        if len(low_snr) > 0:
            errors.append("snr values too low on " + str(len(low_snr)) + " files:")
            for snr_e in low_snr:
                errors.append("    " + snr_e)

        lufs_flux = AudioScrutinizer.compare_lufs(audio_files)

        if len(lufs_flux) > 0:
            for err in lufs_flux:
                errors.append(err)

        if not skip_daisy_checks:
            if audiobook.ncc_count == 0:
                critical_errors.append("No ncc.html found!")
            if audiobook.smil_count == 0:
                critical_errors.append("No smil-files found!")
            if audiobook.dc_identifier != audiobook.filename_prefix:
                warnings.append("Filename prefix differs from dc:identifier")
            if audiobook.audio_file_count != audiobook.smil_count:
                errors.append("Diference in number of audio files compared to smil-files")
            if audiobook.master_smil_count == 0:
                errors.append("No master.smil file found!")
            if audiobook.first_smil_audio_references > 1:
                warnings.append("First heading divided into multiple phrases!")
            if audiobook.ncc_charset != target_text_encoding:
                errors.append("Ncc.html not encoded in " + target_text_encoding + "!")
            if audiobook.dc_title == "":
                errors.append("Name of book not found in metadata!")
            if audiobook.dc_creator == "":
                errors.append("Name of author not found in metadata!")
            if audiobook.ncc_narrator == "":
                errors.append("Name of narrator not found in metadata!")
            if audiobook.dc_date == "":
                errors.append("Date of production not defined in metadata!")
            if audiobook.dc_language == "":
                errors.append("Language of book not defined in metadata!")
            if audiobook.dc_publisher == "":
                errors.append("Publisher not defined in metadata!")
            if audiobook.dc_source == "":
                errors.append("No ISBN found in metadata!")
            if audiobook.ncc_producer == "":
                errors.append("Recording place not defined in metadata!")
                
            if len(audiobook.pagemark_errors) > 0:
                for err in audiobook.pagemark_errors:
                    errors.append("Pagemark at first phrase of heading '" + err[0] + "' (file " + err[1] + ")!")

            if len(audiobook.daisy_validation_errors) > 0:
                errors.append("\n    ERRORS REPORTED BY DAISY VALIDATOR:\n")
                for err in audiobook.daisy_validation_errors:
                    errors.append("    " + err)

            if len(audiobook.daisy_validation_warnings) > 0:
                errors.append("\n    WARNINGS REPORTED BY DAISY VALIDATOR:\n")
                for w in audiobook.daisy_validation_warnings:
                    warnings.append("    " + w)

        ReportGenerator.write_report(audiobook, report_out_path, critical_errors, errors, warnings)

        webbrowser.open(str(report_out_path))

        skip_audio_encoding = False
        if not ConfigGetter.get_configs("encode_audio") == "1":
            skip_audio_encoding = True

        if not skip_daisy_checks and not skip_audio_encoding:
            if audiobook.dc_identifier == "":
                print("Preparing to encode audiobook to output folder " + output_location + "/mp3 ...")
                print("  NOTE! If folder exist, timestamp is added to folder name.")
            else:
                print("Preparing to encode audiobook to output folder " + output_location 
                      + "/" + audiobook.dc_identifier + " ...")
                print("  NOTE! If folder exist, timestamp is added to folder name.")
            ans = input("Continue with encoding of audio? (y/n) (default: No)\n")
            if ans.lower() == "y":
                ncc_path = pathlib.Path.joinpath(pathlib.Path(audiobook.path), "ncc.html")
                encoded_foldername = "mp3"
                if audiobook.dc_identifier != "":
                    encoded_foldername = audiobook.dc_identifier
                encoded_book_location = pathlib.Path.joinpath(pathlib.Path(output_location), encoded_foldername)
                if encoded_book_location.exists():
                    DaisyScrutinizer.encode_audio(str(ncc_path), str(encoded_book_location) + "_" + time_stamp)
                else:
                    DaisyScrutinizer.encode_audio(str(ncc_path), str(encoded_book_location))

    @staticmethod
    def run_validation(path, o_path, r_path):
        d = AudioBook(path)
        CeliaDTBValidator.validate_dtb(d, o_path, r_path)


# MAIN...
if __name__ == "__main__":

    if which("sox") is None:
        input("sox not found from PATH! Please install sox before running validator.")
        sys.exit()
    if which("ffmpeg") is None:
        input("ffmpeg not found from PATH! Please install ffmpeg before running validator.")
        sys.exit()

    arguments = get_args(sys.argv)

    book_path = arguments[0]
    if arguments[1] == "":
        output_path = pathlib.Path("./").absolute()
    else:
        output_path = arguments[1]

    if arguments[2] == "":
        report_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent, "reports")
    else:
        report_path = arguments[2]

    print("CELIA DTB VALIDATOR...")
    print("---------------------------------")
    print("Book path: " + str(book_path))
    print("Output path: " + str(output_path))
    print("Report path: " + str(report_path))
    print("---------------------------------")

    config_file = pathlib.Path.joinpath(pathlib.Path(__file__).parent, "config.txt")

    dtb = AudioBook(str(book_path))
    CeliaDTBValidator.validate_dtb(dtb, str(output_path), str(report_path))

