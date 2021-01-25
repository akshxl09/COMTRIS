FROM 837477/workstation:2.0
MAINTAINER 8374770

COPY ./ /COMTRIS
WORKDIR /COMTRIS

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

WORKDIR /COMTRIS/COMTRIS

CMD ["flask", "test", "flask", "run"]

EXPOSE 80