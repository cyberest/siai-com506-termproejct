# Proejct main
# ===================

import sys

from RedditScraper.config_parser import parse_config
from RedditScraper.web_scraper import RedditScraper
from RedditScraper.data_manager import RedditDataManager


def main(ini_file_path, target_subreddit, export_opt, clean):
    """
    Parameter
    ----------
    ini_file_path: str
        The path to config.ini
    export_opt: str
        Option chosen to export data
    """
    # Parse configurations
    config = parse_config(ini_file_path)

    # Initiate class for web scraper
    scraper = RedditScraper(
        subreddit=target_subreddit,
        base_url=config["BASE_URL"],
        list_moderators=config["LIST_MODERATORS"],
        image_dir=config["IMAGE_DIR"],
        user_agents=config["USER_AGENTS"],
    )

    # Initiate class for database operations
    manager = RedditDataManager(
        subreddit=target_subreddit,
        output_dir=config["OUTPUT_DIR"],
        image_dir=config["IMAGE_DIR"],
        data_dir=config["DATA_DIR"],
        elastic_server=config["ELASTIC_SERVER"],
        nosql_mapping=config["NOSQL_MAPPING"],
    )

    # Cleanup existing data (optional)
    if clean:
        target_table = f"reddit_thread_{target_subreddit}"
        manager.drop_sql_table(target_table) # delete SQL table
        manager.drop_nosql_index(target_table) # delete NoSQL index
        manager.cleanup_image() # delete images downloaded
        manager.cleanup_output() # delete csv outputs
        print(f"Cleanup completed - {target_table}.")

    # Start scraping data
    scrap_result = scraper.scrape_threads()

    # Transfer collected data into the class for database opertaion
    manager.threads = scraper.threads
    data_df = manager.threads_to_df()

    # Export as CSV
    if export_opt == "csv":
        manager.download_csv()
    # Upload DataFrame to SQL database (Sqlite)
    elif export_opt == "sql":
        manager.upload_sql()
    # Upload DataFrame to NoSQL database (Elasticsearch)
    elif export_opt == "nosql":
        manager.upload_nosql()
    elif export_opt == "all":
        manager.download_csv()
        manager.upload_sql()
        manager.upload_nosql()


if __name__ == '__main__':

    # Parse command line options and arguments
    opts = [opt[1:] for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    # Validation
    if len(args) != len(opts):
        raise ValueError("At least one argument is missing, check the README.")
    option_args = dict(zip(opts, args))

    # Export target from user input
    export_opt = option_args['export_opt']
    # If false, do not clean and just accumulate data
    clean = True if option_args['clean'].lower() == 'true' else False

    if not export_opt in ["csv", "sql", "nosql", "all"]:
        print("Please provide correct export option - csv, sql, nosql, all, clean. Aborted.")
    else:
        INI_FILE_PATH = 'config.ini'
        TARGET_SUBREDDIT = 'wallstreetbets'
        main(INI_FILE_PATH, TARGET_SUBREDDIT, export_opt, clean)

