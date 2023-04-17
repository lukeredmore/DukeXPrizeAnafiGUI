#!/bin/bash
cd ~/Desktop/DukeXPrizeAnafiGUI-Local

# In theory, should start olympe shell here (source ~/code/parrot-groundsdk/./products/olympe/linux/env/shell)
# But, all that ensures is the virtual version of python is used, which we can just access directly:

$HOME/code/parrot-groundsdk/out/olympe-linux/pyenv_root/shims/python3 control_gui.py -s ${1:-controller}