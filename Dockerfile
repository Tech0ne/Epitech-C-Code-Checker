FROM ubuntu:22.04

WORKDIR /app

RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y gcc libcsfml-dev python3 python3-pip valgrind gdb binutils hexyl strace

RUN pip3 install rich

COPY ./run.py /opt/run.py
RUN chmod +x /opt/run.py

COPY ./gdbscript.py /opt/gdbscript.py

ENTRYPOINT ["/opt/run.py"]
