#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from ConfigParser import ConfigParser
from optparse import OptionParser
from time import sleep
from os import path

import commands
import requests
import logging
import sys

INACTIVE = []
FORMAT = '%(asctime)-15s %(message)s'
DEFAULT_CONFIG = '/etc/watchman.conf'


def load_config(config_file):
    try:
        config = ConfigParser()
        config.readfp(open(config_file))
    except:
        print('Config file is invalid')
        sys.exit(0)

    options = {}
    for s in config.sections():
        options.setdefault(s, dict(config.items(s)))

    return options


def execute(command):
    commands.getstatusoutput(command)


def check_url(config):
    error = []
    try:
        r = requests.get(config['url'])
        if 'status' in config:
            error.append(r.status_code is not int(config['status']))

        if 'contains' in config:
            error.append(r.text not in config['contains'])

        return (len(error) == 0 or all(error)) and 'execute' in config
    except:
        return True


def check_shell(config):
    error = False
    pid, response = commands.getstatusoutput(config['command'])
    if 'contains' in config:
        error = response not in config['contains']

    return error and 'execute' in config


def work(config):
    for section, cc in config.items():
        if cc['type'] == 'url':
            action = check_url(cc)
        elif cc['type'] == 'shell':
            action = check_shell(cc)

        if section not in INACTIVE and action:
            logging.info("Incident with %s" % section);
            INACTIVE.append(section)
            execute(cc['execute'])

        if section in INACTIVE and action is False:
            logging.info("Incident with %s was resolved" % section);
            INACTIVE.remove(section)


def run():
    parser = OptionParser()
    parser.add_option("-c", "--config",
                      dest="config_path", default=DEFAULT_CONFIG,
                      help="Watchman config file", metavar="FILE")

    (options, args) = parser.parse_args()
    if not path.exists(options.config_path):
        print('Config file not found')
        sys.exit(0)

    config = load_config(options.config_path)

    try:
        watchman = config.pop('watchman')
    except KeyError:
        print('Config file is invalid')
        sys.exit(0)

    # Logging all stuff
    logging.basicConfig(
        level=watchman.get('log_level', 'DEBUG'),
        filename=watchman['log'],
        format=FORMAT)
    logging.getLogger("requests").setLevel(logging.CRITICAL)

    while True:
        work(config)
        sleep(float(watchman.get('timeout', 1000)) / 1000)


def main():
    try:
        run()
    except KeyboardInterrupt:
        print('Exit')


if __name__ == '__main__':
    main()
