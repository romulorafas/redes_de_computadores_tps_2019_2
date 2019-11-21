#!/bin/sh
set -eu

exe1="python3.5 ../my_router.py"
exe2="python3.5 ../router.pyc"


tmux split-pane -v $exe1 --addr 127.0.1.1 --update-period 5 --startup-commands 1.txt &
tmux select-layout even-vertical

tmux split-pane -v $exe2 --addr 127.0.1.2 --update-period 5 --startup-commands 2.txt &
tmux select-layout even-vertical

tmux split-pane -v $exe1 --addr 127.0.1.3 --update-period 5 --startup-commands 3.txt &
tmux select-layout even-vertical

tmux split-pane -v $exe2 --addr 127.0.1.4 --update-period 5 --startup-commands 4.txt &
tmux select-layout even-vertical

tmux split-pane -v $exe1 --addr 127.0.1.5 --update-period 5 --startup-commands 5.txt &
tmux select-layout even-vertical

tmux split-pane -v $exe2 --addr 127.0.1.6 --update-period 5 --startup-commands 6.txt &
tmux select-layout even-vertical
