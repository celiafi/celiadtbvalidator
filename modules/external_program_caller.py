import subprocess


class ExternalProgramCaller:

    @staticmethod
    def run_external_command(cmd):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        run_cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=si)
        cmd_output = run_cmd.communicate()[0].decode(encoding="utf8", errors="replace")
        return cmd_output
