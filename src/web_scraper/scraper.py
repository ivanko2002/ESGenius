import os, sys, json
import logging, traceback, logging.config
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
sys.path.insert(1, '..\src')

class WebScraper:
    def __init__(self, config_folder, download_path=None):
        self.logger = logging.getLogger(__name__)
        self.download_path = download_path if download_path else os.path.join(Path.home(), "Downloads")
        self.driver = None
        self.config_folder = config_folder

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        self.driver = webdriver.Chrome(options=chrome_options)

    def scrape_files(self, url, cik):
        try:
            self.logger.info(f"Start scraping for {cik}")
            self.setup_driver()
            self.driver.get(url)
            body_html = self.driver.find_element(By.ID, 'results-grid').get_attribute('innerHTML')
            soup = BeautifulSoup(body_html, 'html.parser')
            filetype_elements = soup.select('td.filetype')
            # get accession number for files
            data_adsh_list = [element.find('a')['data-adsh'] for element in filetype_elements if element.find('a')]
            self.logger.info(f"{len(data_adsh_list)} files founded")
            for accession_number in data_adsh_list:
                index_key = accession_number.split('-')[0]
                accession_number_without_zeros = index_key.lstrip('0')
                accession_number_without_dashes = accession_number.replace('-', '')
                data_file_url = f"https://www.sec.gov/Archives/edgar/data/{accession_number_without_zeros}/{accession_number_without_dashes}/{accession_number}.txt"
                # start downloading the file
                self.download_files(data_file_url)
                self.logger.info(f"Downloaded: {accession_number_without_zeros}/{accession_number_without_dashes}/{accession_number}.txt")

        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}", exc_info=True)
            self.logger.error(f"Traceback: {traceback.format_exc()}")

        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("WebDriver closed")
            self.logger.info(f"End scraping for {cik}")

    def download_files(self, data_file_url):
        self.driver.get(data_file_url)
        body_content = self.driver.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML')
        soup = BeautifulSoup(body_content, 'html.parser')
        file_name = data_file_url.split("/")[-1]
        # output as txt file
        with open('{}'.format(os.path.join(self.download_path, file_name)), mode='wt', encoding='utf-8') as file:
            file.write(soup.text)

    def run(self):
        with open(os.path.join(self.config_folder, 'name_to_cik.json'), 'r') as file:
            data = json.load(file)
        cik_list = [entry['CIK'].zfill(10) for entry in data]

        #for i in range(len(cik_list)):
        for i in range(10):
            url = f"https://www.sec.gov/edgar/search/#/category=custom&entityName={cik_list[i]}&forms=10-K"
            self.scrape_files(url, cik_list[i])

        


