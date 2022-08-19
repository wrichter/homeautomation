FROM registry.access.redhat.com/ubi8/python-39:latest

RUN pip3 install requests

COPY cputemp.py .

CMD python3 cputemp.py