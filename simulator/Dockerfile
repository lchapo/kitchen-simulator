FROM python:3.8.2-slim

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN mkdir /simulator/
WORKDIR /simulator/
COPY . /simulator/

ENV PYTHONPATH /simulator/

CMD ["python", "./order_simulator.py"]
