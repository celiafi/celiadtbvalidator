from modules.external_program_caller import ExternalProgramCaller
import re
import pathlib
from modules.config_getter import ConfigGetter


def get_peak(raw_output):
    peak = 0.0
    for line in reversed(raw_output):
        if re.search(r".+Peak", line):
            line = re.sub(r".+Peak: *", "", line)
            line = re.sub(r" dBFS", "", line)
            peak = round(float(line),2)
            break
    return peak


class AudioScrutinizer:

    @staticmethod
    def get_stats(f_path):
        print("     Calculating lufs & peak levels")

        # f_path = str(pathlib.Path(f_path).absolute())
        # input(f_path)

        stats = []

        lufs = 0.0
        pkdb = 0.0
        tpkdb = 0.0
        snr = 0.0
        kbps = 0.0

        # general stats with ffmpeg
        ffmpeg_cmd_lufs = 'cmd /c ffmpeg -nostats -i "' + f_path + '" -filter_complex ebur128=peak=true -f null - 2>&1'
        ffmpeg_cmd_stats = 'cmd /c ffmpeg -i "' + f_path + '" -af astats -f null - 2>&1'

        raw_output_lufs = ExternalProgramCaller.run_external_command(ffmpeg_cmd_lufs).splitlines()
        raw_output_stats = ExternalProgramCaller.run_external_command(ffmpeg_cmd_stats).splitlines()



        rms_trough_db = 0.0
        rms_peak_db = 0.0

        for line in reversed(raw_output_lufs):
            if re.search(r".+Peak", line):
                line = re.sub(r".+Peak: *", "", line)
                tpkdb = float(re.sub(r" dBFS", "", line))
            if re.search(r" *I: .+ LUFS", line):
                line = re.sub(r" *I: *", "", line) 
                line = re.sub(r" LUFS", "", line)
                lufs = round(float(line), 2)
                break

        for line in raw_output_lufs:
            if re.search(r".+bitrate:", line):
                line = re.sub(r".+bitrate: *", r"", line)
                line = re.sub(r" kb.+", r"", line)
                kbps = float(line)
                break
            
        for line in reversed(raw_output_stats):
            if re.search(r".+Peak level dB", line):
                line = re.sub(r".+Peak level dB: ", "", line)
                pkdb = round(float(line),2)
                break
            if re.search(r".+RMS trough dB", line):
                line = re.sub(r".+RMS trough dB: ", "", line)
                rms_trough_db = round(float(line),2)

            if re.search(r".+RMS peak dB", line):
                line = re.sub(r".+RMS peak dB: ", "", line)
                rms_peak_db = round(float(line),2)
            
        
        
        
            # snr (sox) example:
            # a: RMS Pk dB      -9.04
            # b: RMS Tr dB     -91.69
            # -> snr = a - b


        snr = rms_peak_db - rms_trough_db

        stats.append(lufs)
        stats.append(pkdb)
        stats.append(tpkdb)
        stats.append(snr)
        stats.append(kbps)

        return stats

    @staticmethod
    def find_silence(f_path):
        print("     Checking for unexpected silences at start, end or middle of file")
        silence_db = ConfigGetter.get_configs("silence_db")
        if silence_db == "":
            silence_db = "-26"

        try:
            silence_db = int(silence_db)
        except:
            silence_db = -26

        silence_check = []

        # Silence at start of audiofile
        # sox PATH -n trim 0 0:01.001 stats 2>&1

        no_start_silence = True
        start_silence_max = ConfigGetter.get_configs("start_silence_max")
        if start_silence_max == "":
            start_silence_max = "0:01.001"
        
        start_silence_max_ffmpeg_cmd = 'cmd /c ffmpeg -ss 00:00:00 -nostats -i "' + f_path + '" -to 00:0' + start_silence_max + ' -filter_complex ebur128=peak=true -f null - 2>&1'
        
        raw_output = ExternalProgramCaller.run_external_command(start_silence_max_ffmpeg_cmd).splitlines()
        if get_peak(raw_output) < silence_db:
            no_start_silence = False

        # Minimum silence at end of file
        # sox PATH -n reverse trim 0 0:01.801 reverse stats 2>&1

        silence_at_end = True
        end_silence_min = ConfigGetter.get_configs("end_silence_min")
        if end_silence_min == "":
            end_silence_min = "0:01.801"

        end_silence_min_ffmpeg_cmd = 'cmd /c ffmpeg -sseof -00:0' + end_silence_min + ' -nostats -i "' + f_path + '" -filter_complex ebur128=peak=true -f null - 2>&1'

        raw_output = ExternalProgramCaller.run_external_command(end_silence_min_ffmpeg_cmd).splitlines()

        if get_peak(raw_output) > silence_db:
            silence_at_end = False

        # Maximum allowed silence at end of file
        # sox PATH -n reverse trim 0 0:15.001 reverse stats 2>&1

        no_unexpected_silence_at_end = True
        end_silence_max = ConfigGetter.get_configs("end_silence_max")
        if end_silence_max == "":
            end_silence_max = "0:15.001"

        end_silence_max_ffmpeg_cmd = 'cmd /c ffmpeg -sseof -00:0' + end_silence_max + ' -nostats -i "' + f_path + '" -filter_complex ebur128=peak=true -f null - 2>&1'

        raw_output = ExternalProgramCaller.run_external_command(end_silence_max_ffmpeg_cmd).splitlines()

        if get_peak(raw_output) < silence_db:
            no_unexpected_silence_at_end = False

        # Unexpected mid silences
        # ffmpeg -nostats -i TIEDOSTO -af silencedetect=noise=-26dB:d=5 -f null - 2>&1
        mid_silence_max = ConfigGetter.get_configs("mid_silence_max")
        if mid_silence_max == "":
            mid_silence_max = "7"
        mid_silences = []
        mid_silence_cmd = 'cmd /c ffmpeg -nostats -i "' \
                          + f_path + '" -af silencedetect=noise=' + str(silence_db) + 'dB:d=' \
                          + mid_silence_max + ' -f null - 2>&1 '

        raw_output = ExternalProgramCaller.run_external_command(mid_silence_cmd).splitlines()

        for line in raw_output:
            # print(line)
            if re.search(r".+silence_end.+", line):
                line = re.sub(r".+silence_end: ", r"", line)
                pieces = line.split(" | ")
                silence_length = re.sub(r"silence_duration: ", r"", pieces[1])
                silence_at = float(pieces[0])
                silence_at_hour = int(silence_at // 3600)
                silence_at_hour_str = str(silence_at_hour)
                silence_at_min = int((silence_at - silence_at_hour * 60 * 60) // 60)
                if silence_at_min < 10:
                    silence_at_min_str = "0" + str(silence_at_min)
                else:
                    silence_at_min_str = str(silence_at_min)
                silence_at_sec_ms = silence_at - (silence_at_hour * 60 * 60) - (silence_at_min * 60)
                silence_at_sec_ms_tmp = str(silence_at_sec_ms).split(".")
                silence_at_sec = int(silence_at_sec_ms_tmp[0])
                silence_at_ms = float("0." + silence_at_sec_ms_tmp[1])
                # silence_at_ms = round(silence_at_ms, 3)
                silence_at_ms = float(format(silence_at_ms, ".3f"))
                silence_at_sec_ms = silence_at_sec + silence_at_ms
                if silence_at_sec_ms < 10:
                    silence_at_sec_ms_str = "0" + format(silence_at_sec_ms, ".3f")
                else:
                    silence_at_sec_ms_str = format(silence_at_sec_ms, ".3f")
                silence_at_fmt = silence_at_hour_str + ":" + silence_at_min_str + ":" + silence_at_sec_ms_str

                mid_silences.append("Unexpected silence found at " + silence_at_fmt
                                    + " (Silence duration: " + format(float(silence_length), ".3f") + " sec)")

        silence_check.append(no_start_silence)
        silence_check.append(silence_at_end)
        silence_check.append(no_unexpected_silence_at_end)
        silence_check.append(mid_silences)

        return silence_check

    @staticmethod
    def compare_lufs(audio_files):
        max_volume_level_flux = ConfigGetter.get_configs("max_volume_level_flux")
        try:
            max_volume_level_flux = int(max_volume_level_flux)
        except:
            max_volume_level_flux = 1

        lufs_flux = []
        i = 1
        while i < len(audio_files):
            audio_f_comp = audio_files[i - 1]
            if (audio_f_comp.lufs * -1) - (audio_files[i].lufs * -1) > (1 * max_volume_level_flux) \
                    or (audio_f_comp.lufs * -1) - (audio_files[i].lufs * -1) < (-1 * max_volume_level_flux):
                lufs_flux.append("Noticeable change in volume compared to previous audiofile on "
                                 + audio_files[i].name + "." + audio_files[i].f_type + "! (Change "
                                 + str(audio_f_comp.lufs) + " LUFS -> " + str(audio_files[i].lufs) + " LUFS.)")
            i += 1

        return lufs_flux
