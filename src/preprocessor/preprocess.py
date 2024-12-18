import logging, traceback, logging.config
import os, glob, re

class Preprocessor:
    def __init__(self, config_folder, download_path=None):
        self.logger = logging.getLogger(__name__)
        src_folder = os.path.dirname(os.path.abspath(__file__))
        self.data_folder = os.path.join(os.path.dirname(src_folder), 'data')

        self.download_path = download_path if download_path else self.data_folder
        self.driver = None
        self.config_folder = config_folder

    def remove_ascii_segments(self, text):
        patterns = ["<TYPE>GRAPHIC", "<TYPE>ZIP", "<TYPE>EXCEL", "<TYPE>JSON", "<TYPE>PDF"]
        for pattern in patterns:
            text = re.sub(f"<TYPE>{pattern}.*?</TYPE>", "", text, flags=re.DOTALL)
        return text

    def remove_specific_tags(self, text):
        tags = ["DIV", "TR", "TD", "FONT"]
        for tag in tags:
            text = re.sub(f"</?{tag}.*?>", "", text, flags=re.DOTALL)
        return text

    def remove_xml_documents(self, text):
        text = re.sub(r"<\?xml.*?\?>", "", text, flags=re.DOTALL)
        return text

    def remove_xbrl(self, text):
        text = re.sub(r"<XBRL.*?>.*?</XBRL>", "", text, flags=re.DOTALL)
        return text

    def remove_sec_headers(self, text):
        text = re.sub(r".*?</SEC-HEADER>", "", text, flags=re.DOTALL)
        text = re.sub(r".*?</IMS-HEADER>", "", text, flags=re.DOTALL)
        return text

    def replace_nbsp(self, text):
        text = text.replace("&NBSP;", " ").replace("&#160;", " ")
        return text

    def replace_amp(self, text):
        text = text.replace("&AMP;", "&").replace("&#38;", "&")
        return text

    def remove_extended_char_refs(self, text):
        text = re.sub(r"&#[0-9]+;", "", text)
        return text

    def remove_markup_tags(self, text):
        text = re.sub(r"<.*?>", "", text)
        return text

    def remove_excess_linefeeds(self, text):
        text = re.sub(r"\n+", "\n", text)
        return text

    def clean_document(self, file_content):
        file_content = self.remove_ascii_segments(file_content)
        file_content = self.remove_specific_tags(file_content)
        file_content = self.remove_xml_documents(file_content)
        file_content = self.remove_xbrl(file_content)
        file_content = self.remove_sec_headers(file_content)
        file_content = self.replace_nbsp(file_content)
        file_content = self.replace_amp(file_content)
        file_content = self.remove_extended_char_refs(file_content)
        file_content = self.remove_markup_tags(file_content)
        file_content = self.remove_excess_linefeeds(file_content)
        return file_content

    def run(self):
        for folder_name in sorted(os.listdir(self.data_folder)):
            folder_path = os.path.join(self.data_folder, folder_name)
            
            # Check if the folder is a directory
            if os.path.isdir(folder_path):
                print(f"Reading files in folder: {folder_name}")
                
                # Get all .txt files in the current folder
                txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
                
                for txt_file in txt_files:
                    try:
                        with open(txt_file, 'wt', encoding='utf-8') as file:
                            content = file.readlines()
                            for i in range(len(content)):
                                content[i] = self.clean_document(content[i])
                            file.write('\n'.join(content))

                    except Exception as e:
                        self.logger.error(f"An error occurred: {str(e)}", exc_info=True)
                        self.logger.error(f"Traceback: {traceback.format_exc()}")
