from modules.audio_file import AudioFile
from modules.config_getter import ConfigGetter


class ReportGenerator:

    @staticmethod
    def write_report(audiobook, report_out_path, critical_errors, errors, warnings):
        validation_report = open(str(report_out_path), "x", encoding="utf-8")
        skip_daisy_checks = False
        if not ConfigGetter.get_configs("daisy_validation") == "1":
            skip_daisy_checks = True

        skip_audio_checks = False
        if not ConfigGetter.get_configs("audio_validation") == "1":
            skip_audio_checks = True

        validation_report.write("<!DOCTYPE html>\n"
                                + "<html lang=""en"">\n"
                                + "<head>\n"
                                + "<meta charset=""UTF-8"">\n"
                                + "<title>VALIDATION REPORT</title>\n"
                                + "</head>\n"
                                + "<body>\n")

        if not skip_daisy_checks:
            validation_report.write("<h1>Validation report for dtb " + audiobook.dc_title + " / "
                                    + audiobook.dc_creator + " (" + audiobook.dc_identifier + ")</h1>\n\n")

            validation_report.write("<p style=""font-size:22px;"">\n"
                                    + "<b>Title:</b> " + audiobook.dc_title + "<br />\n"
                                    + "<b>Author:</b> " + audiobook.dc_creator + "<br />\n"
                                    + "<b>Narrator:</b> " + audiobook.ncc_narrator + "<br />\n"
                                    + "<b>Id:</b> " + audiobook.dc_identifier + "<br /></p>\n\n")
        else:
            validation_report.write("<h1>Validation report for dtb " + audiobook.path + "</h1>")

        validation_report.write("<h2>Validation summary:</h2>\n\n")

        if len(critical_errors) > 0:
            validation_report.write("<h3>Critical errors:</h3>\n")

            validation_report.write("<pre style=""font-size:18px;"">\n")

            for err in critical_errors:
                validation_report.write("    " + err + "\n")
            validation_report.write("</pre>\n\n")

        if len(errors) > 0:
            validation_report.write("<h3>Errors:</h3>\n")

            validation_report.write("<pre style=""font-size:18px;"">\n")

            for err in errors:
                validation_report.write("    " + err + "\n")
            validation_report.write("</pre>\n\n")

        if len(warnings) > 0:
            validation_report.write("<h3>Warnings:</h3>\n")

            validation_report.write("<pre style=""font-size:18px;"">\n")

            for err in warnings:
                validation_report.write("    " + err + "\n")
            validation_report.write("</pre>\n\n")

        if len(critical_errors) == 0 and len(errors) == 0 and len(warnings) == 0:
            validation_report.write("<p style=""font-size:22px;"">\n"
                                    + "No errors or warnings found. Congratulations!</p>\n\n")

        validation_report.write("<h2>Detailed information</h2>\n")

        if not skip_audio_checks:
            validation_report.write("<h3>Audio stats</h3>\n")
            validation_report.write("<pre style=""font-size:18px;"">\n")
            validation_report.write("    Avg. LUFS: " + format(audiobook.lufs, ".2f") + " LUFS\n")
            validation_report.write("    Avg. pkdb: " + format(audiobook.pkdb, ".2f") + " dB\n")
            validation_report.write("    Avg. tpkdb: " + format(audiobook.tpkdb, ".2f") + " dB\n")
            validation_report.write("    Avg. snr: " + format(audiobook.snr, ".2f") + " dB\n")
            validation_report.write("    KBPS: " + format(audiobook.kbps, ".0f") + "\n\n")

            for audio_f in audiobook.files:
                if isinstance(audio_f, AudioFile):
                    # format(float(silence_length), ".3f")

                    validation_report.write("    " + audio_f.name + "." + audio_f.f_type
                                            + ", " + format(audio_f.lufs, ".2f") + " LUFS, "
                                            + "peak " + format(audio_f.pkdb, ".2f")
                                            + " dB, tpkdb " + format(audio_f.tpkdb, ".2f")
                                            + " dB, snr " + format(audio_f.snr, ".2f") + " dB\n")

            validation_report.write("</pre>\n\n")

        if not skip_daisy_checks:
            validation_report.write("<h3>Filestructure</h3>\n")

            validation_report.write("<pre style=""font-size:18px;"">\n")
            validation_report.write("    <b>ncc.html files:</b> " + str(audiobook.ncc_count) + "\n")
            validation_report.write("    <b>audiofiles:</b> " + str(audiobook.audio_file_count) + "\n")
            validation_report.write("    <b>smil-files:</b> " + str(audiobook.smil_count) + "\n")
            validation_report.write("    <b>master.smil files:</b> " + str(audiobook.master_smil_count) + "\n")
            validation_report.write("    <b>image files:</b> " + str(audiobook.image_count) + "\n")
            validation_report.write("    <b>css files:</b> " + str(audiobook.css_count) + "\n")
            validation_report.write("    <b>other files:</b> " + str(audiobook.other_filetype_count) + "\n")
            validation_report.write("</pre>\n\n")

            validation_report.write("<h3>Metadata</h3>\n")

            validation_report.write("<pre style=""font-size:18px;"">\n")
            validation_report.write("    <b>dc:title:</b> " + audiobook.dc_title + "\n")
            validation_report.write("    <b>dc:creator:</b> " + audiobook.dc_creator + "\n")
            validation_report.write("    <b>dc:date:</b> " + audiobook.dc_date + "\n")
            validation_report.write("    <b>dc:identifier:</b> " + audiobook.dc_identifier + "\n")
            validation_report.write("    <b>dc:language:</b> " + audiobook.dc_language + "\n")
            validation_report.write("    <b>dc:publisher:</b> " + audiobook.dc_publisher + "\n")
            validation_report.write("    <b>dc:source:</b> " + audiobook.dc_source + "\n")
            validation_report.write("    <b>ncc:narrator:</b> " + audiobook.ncc_narrator + "\n")
            validation_report.write("    <b>ncc:producer:</b> " + audiobook.ncc_producer + "\n")
            validation_report.write("    <b>dc:format:</b> " + audiobook.dc_format + "\n")
            validation_report.write("    <b>ncc:generator:</b> " + audiobook.ncc_generator + "\n")
            validation_report.write("    <b>prod:prevGenerator:</b> " + audiobook.prod_prev_generator + "\n")
            validation_report.write("    <b>ncc:pageNormal:</b> " + audiobook.ncc_page_normal + "\n")
            validation_report.write("    <b>ncc:pageFront:</b> " + audiobook.ncc_page_front + "\n")
            validation_report.write("    <b>ncc:pageSpecial:</b> " + audiobook.ncc_page_special + "\n")
            validation_report.write("    <b>ncc:depth:</b> " + audiobook.ncc_depth + "\n")
            validation_report.write("    <b>ncc:charset:</b> " + audiobook.ncc_charset + "\n")
            validation_report.write("    <b>ncc:multimediaType:</b> " + audiobook.ncc_multimedia_type + "\n")
            validation_report.write("    <b>ncc:tocItems:</b> " + audiobook.ncc_toc_items + "\n")
            validation_report.write("    <b>ncc:totalTime:</b> " + audiobook.ncc_total_time + "\n")
            validation_report.write("    <b>ncc:files:</b> " + audiobook.ncc_files + "\n")
            validation_report.write("</pre>\n\n")

        validation_report.write("<h2>END OF VALIDATION REPORT</h2>\n\n")

        validation_report.write('<p style="width: 100%; text-align: center; font-size: 12px; font-style: italic; font-weight: bold;">CeliaDTBValidator v. 0.9.3beta1</p>	\n')

        validation_report.write("</body>\n"
                                + "</html>")

        validation_report.close()
