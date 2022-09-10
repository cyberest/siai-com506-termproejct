from configparser import ConfigParser
from ast import literal_eval

def parse_config(config_path):
    """Parse config.ini.
    Parameter
    ----------
    config_path: str
        The path to config.ini
    Return
    -------
    dict
        A dictionary containing configuration parameters
    """

    parser = ConfigParser()
    parser.read(config_path)

    # Use literal_eval for iterative objects
    config_dict = {
        'DATA_DIR': parser.get('filesystem', 'DATA_DIR'),
        'IMAGE_DIR': parser.get('filesystem', 'IMAGE_DIR'),
        'BASE_URL': parser.get('filesystem', 'BASE_URL'),
        'USER_AGENTS': literal_eval(parser.get('webscraping', 'USER_AGENTS')),
        'LIST_MODERATORS': literal_eval(parser.get('site_specific', 'LIST_MODERATORS')),
    }
    return config_dict


if __name__ == '__main__':
    pass