from modules.generic_file import GenericFile
from modules.audio_scrutinizer import AudioScrutinizer


class AudioFile(GenericFile):

    def __init__(self, path, name, f_type):
        super().__init__(path, name, f_type)

        print("    Counting audio stats...")
        stats = AudioScrutinizer.get_stats(self.path)
        silences = AudioScrutinizer.find_silence(self.path)
        print("    DONE!")

        self.lufs = stats[0]
        self.pkdb = stats[1]
        self.tpkdb = stats[2]
        self.snr = stats[3]
        self.kbps = stats[4]

        self.no_start_silence = silences[0]
        self.end_silence = silences[1]
        self.no_unexpected_end_silence = silences[2]
        self.mid_silences = silences[3]
