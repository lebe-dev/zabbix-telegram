import argparse

import os
import sys
import logging
import logging.config
import logging.handlers

from telegram_api import TelegramApi

from ConfigParser import ConfigParser

VERSION = '1.0.0'

TELEGRAM_API_HOST = 'api.telegram.org'

USER_NOT_FOUND = "User not found"


class InvalidConfigurationException(Exception):
    pass


class Application:
    def __init__(self, config, opts):
        self.logger = logging.getLogger("logfile")

        self.config = config

        self.api_key = None
        self.target_id = None

        self.load_configuration(opts.to)

    def load_configuration(self, target_user):
        try:
            self.api_key = self.config.get('telegram-bot', 'api-key')
        except:
            raise InvalidConfigurationException("api-key not found")

        try:
            self.target_id = self.config.get('allowed-users', target_user)
        except:
            raise InvalidConfigurationException("user '%s' not found, check configuration" % target_user)


def compile_config(config_file_path):
    if not config_file_path:
        config_file_path = 'zabbix-telegram.conf'

    config = ConfigParser()

    if os.path.isfile(config_file_path):
        try:
            config.read(config_file_path)
        except:
            raise IOError("Unable to read from file: %s" % config_file_path)
    else:
        raise IOError("Configuration file not found: %s" % config_file_path)

    return config


if __name__ == '__main__':
    logging.config.fileConfig('/usr/lib/zabbix/alertscripts/logging.conf')
    log = logging.getLogger('logfile')

    parser = argparse.ArgumentParser(usage='<to> "<subject>" "<message>"',
                                     description='Zabbix script for notifications via Telegram Messenger',
                                     epilog='site: github.com/lebe-dev/zabbix-telegram')

    parser.add_argument('to', help="user alias from configuration file")
    parser.add_argument('subject', help="subject of message")
    parser.add_argument('message', help="text of message")

    parser.add_argument('-v', '--version', action="version", help="show version")

    parser.add_argument("-c", "--config", dest="config_file_path", help="path to configuration file")

    options = parser.parse_args(sys.argv[1:])

    try:
        config = compile_config(options.config_file_path)

        app = Application(config, options)

        api = TelegramApi(TELEGRAM_API_HOST, app.api_key)

        api.get_updates()

        api.send_message(app.target_id, options.subject, options.message)

    except ValueError as e:
        log.error(e.message)

    except IOError as e:
        log.error(e.message)

    except InvalidConfigurationException as e:
        log.error(e.message)
