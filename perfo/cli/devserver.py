# -*- coding: utf-8 -*-
from perfo.cli import main

def run(app, args):
    app.run(debug=True)

if __name__ == '__main__':
    main(run)
