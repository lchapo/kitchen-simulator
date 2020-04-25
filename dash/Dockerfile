FROM conda/miniconda3

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN mkdir /dash/
WORKDIR /dash/
COPY . /dash/

ENV PYTHONPATH /dash/

CMD ["python", "./app.py"]
