from modules.config_getter import ConfigGetter
import pathlib
from shutil import which

class PathChecker:


    @staticmethod
    def check_audio_ext_paths():
        ffmpeg_path = ConfigGetter.get_configs("ffmpeg_path")
        if which(ffmpeg_path) is None:
            print("FFmpeg not found at " + str(ffmpeg_path))
            return False
        else:
            return True

    @staticmethod
    def check_daisy_ext_paths():
        programs_found = True
        
        pipeline_path = pathlib.Path(ConfigGetter.get_configs("pipeline_path"))
        if not pipeline_path.exists():
            programs_found = False
            print("Pipeline not found at " + str(pipeline_path))

        java_path = ConfigGetter.get_configs("java_path")
        if which(java_path) is None:
            programs_found = False
            print("Java not found at " + str(java_path))
        
        return programs_found
