# Add this alias to your bashrc

alias saferunc='sudo docker run -it --rm -v /tmp/.X11-unix/:/tmp/.X11-unix/ -v ./:/app/ -e "DISPLAY=${DISPLAY:-:0.0}" saferunc:latest'
