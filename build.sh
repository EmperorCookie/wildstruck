#!/bin/bash
pyinstaller --specpath ./artifacts --workpath ./artifacts -n wildstruck --distpath ./dist -F main.py
