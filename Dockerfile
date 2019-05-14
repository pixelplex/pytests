FROM ubuntu:18.04

WORKDIR /home/

RUN apt-get update && apt-get install -y git make gcc g++ libffi-dev libssl-dev python-dev python3-dev python3-pip

COPY ./common /home/common
COPY ./fixtures /home/fixtures
COPY ./resources /home/resources
COPY ./suites /home/suites
COPY ./.flake8 /home/
COPY ./__init__.py /home/
COPY ./project.py /home/
COPY ./requirements.txt /home/

RUN pip3 install -r requirements.txt

RUN git clone https://github.com/vishnubob/wait-for-it.git

CMD ["lcc", "run", "--exit-error-on-failure"]
