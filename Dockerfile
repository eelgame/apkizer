FROM python:3.9.15

ADD apkizer.py /w/
ADD requirements.txt /w/
WORKDIR /w

RUN pip3 install -r requirements.txt

CMD []
ENTRYPOINT ["python", "apkizer.py"]