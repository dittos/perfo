# -*- coding: utf-8 -*-
import argparse
from perfo import create_app

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', dest='config_path', default='perfo.conf.py')

def main(handler):
    args = parser.parse_args()
    app = create_app(args.config_path)
    with app.app_context():
        handler(app, args)
