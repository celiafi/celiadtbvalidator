import pathlib
import re
import webbrowser


def generate_configs():
    config_file = pathlib.Path.joinpath(pathlib.Path(__file__).parents[1], "config.txt")
    new_config_file = open(str(config_file), "x")
    configs = ["# GENERAL SETTINGS",
               "# To disable set value to 0, to enable set to 1.",
               "audio_validation = 1",
               "daisy_validation = 1",
               "open_reports_after_validation = 1",
               "",
               "",
               "# AUDIO ENCODING SETTINGS",
               "# Note: Audio encoding settings only aply if daisy validation is on.",
               "# To completely disable audio encoding, set value to 0",
               "encode_audio = 1",
               "# Valid values: 32, 48, 64 & 128 (Default 48)",
               "target_kbps = 48",
               "",
               "",
               "# VALIDATION SETTINGS",
               "target_text_encoding = utf-8",
               "lufs_min = -20",
               "lufs_max = -17",
               "pkdb_min = -2",
               "pkdb_max = 0",
               "tpkdb_min = -2",
               "tpkdb_max = 0",
               "snr_min = 45",
               "kbps_min = 32",
               "kbps_max = 48",
               "",
               "# Silence db determines what level is to be considered silence/sound.",
               "# Anything below this value is considered silence and anything higher than this sound.",
               "silence_db = -26",
               "",
               "# Minimum pause at end of file (ie. between chapters) (Format min:ss.ms)",
               "end_silence_min = 0:01.801",
               "# Maximum allowed silence at end of file  (Format min:ss.ms).",
               "end_silence_max = 0:15.001",
               "# Maximum allowed pause at start of file (Format min:ss.ms)",
               "start_silence_max = 0:01.001",
               "",
               "# Determine what is considered unexpectedly long pause at middle of audiofile (ie. middle of a "
               "chapter).",
               "# If longer pauses are normal part of the book (for dramatic reasons etc.), this value should be set",
               "# to a fairly high number to avoid unwanted error messages.",
               "# Value is set in seconds",
               "mid_silence_max = 7",
               "",
               "# Determine how much LUFS value can vary from one audiofile to another audiofile "
               "(ie. between chapters)",
               "max_volume_level_flux = 1",
               "",
               "",
               "# PATHS",
               r"pipeline_path = C:\Program Files (x86)\DAISY Pipeline\plugins\org.daisy.pipeline_1.0.12",
               "ffmpeg_path = ffmpeg",
               "java_path = java",
               "",
               ""]
    for conf in configs:
        new_config_file.write(conf + "\n")
    new_config_file.close()


class ConfigGetter:

    @staticmethod
    def open_config_file():
        config_file = pathlib.Path.joinpath(pathlib.Path(__file__).parents[1], "config.txt")
        if config_file.exists():
            webbrowser.open(str(config_file))
        else:
            print("No config file found! Generating new config.txt")
            generate_configs()
            if config_file.exists():
                webbrowser.open(str(config_file))

    @staticmethod
    def get_configs(conf):
        config = ""
        config_file = pathlib.Path.joinpath(pathlib.Path(__file__).parents[1], "config.txt")
        if not config_file.exists():
            print("No config file found! Generating new config.txt")
            generate_configs()
        configs = open(str(config_file), "r").read().splitlines()

        for line in configs:
            if re.search(r"^" + conf + " = ", line):
                config = re.sub(r".+= ", "", line)
                # print(config)

        return config
