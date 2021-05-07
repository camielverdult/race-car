FROM jjanzic/docker-python3-opencv

WORKDIR /racex

COPY . .

RUN pip3 install -r requirements.txt

# 1/FPS is the time the script will sleep for 
# before re-running hough transform and updating values
ENV FPS 10

CMD [ "python3", "main.py" ]