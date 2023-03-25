FROM 4pdosc/openmldb:0.7.2

ADD ./requirements.txt /work/
ENV PYTHONWARNINGS="ignore:Unverified HTTPS request"
RUN pip install --upgrade pip && \
    pip install -r /work/requirements.txt -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com/simple

WORKDIR /work/adops
