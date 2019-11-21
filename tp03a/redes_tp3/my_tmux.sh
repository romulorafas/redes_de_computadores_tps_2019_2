#!/bin/sh
set -eu

exe_client="python client.py"
exe_server="python server.py"

tmux split-pane -v $exe_server 5151 &

tmux split-pane -v $exe_client 5152 127.0.0.1 5151 & tmux select-layout even-vertical
tmux split-pane -v $exe_client 5153 127.0.0.1 5151 & tmux select-layout even-vertical
tmux split-pane -v $exe_client 5154 127.0.0.1 5151 & tmux select-layout even-vertical
