FROM jjanzic/docker-python3-opencv

WORKDIR /racex

RUN git clone https://github.com/camielverdult/race-car

WORKDIR /racex/race-car

RUN pip3 install -r requirements.txt

ENV FPS 10

ENTRYPOINT [ "python3 main.py" ]