import os, sys
import logging, logging.config
from argparse import ArgumentParser
from web_scraper import WebScraper
#sys.path.insert(1, '..\src')

parser = ArgumentParser(description='Web Scraper Parameters')
parser.add_argument("--download_path", type=str, default=r"", help='output absolute path')
parser.add_argument("--log_config_file", type=str, default="parser_logging.conf", help='absolute path of log config')
args = parser.parse_args()

if __name__ == "__main__":
    src_folder = os.path.dirname(os.path.abspath(__file__))
    config_folder = os.path.join(os.path.dirname(src_folder), 'config')
    log_config_file = os.path.join(config_folder, args.log_config_file)
    if not os.path.exists(log_config_file):
        print(f'Log config file: {log_config_file} does not exist. Please check!')
        sys.exit(-1)

    logging.config.fileConfig(log_config_file)
    logger = logging.getLogger(__name__)

    # main starts
    logger.info('Scraper Main starts')
    web_scraper = WebScraper(config_folder=config_folder, download_path=args.download_path)
    web_scraper.run()
    logger.info("Main ends")