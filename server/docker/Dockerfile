FROM centos:7

RUN yum clean all && yum update -y && yum install -y sudo git epel-release && yum clean all
RUN yum install -y python34 && yum clean all

# Sudo complains about not having TTY unless this is done (see rhbz#1020147)
RUN echo 'Defaults !requiretty' >> /etc/sudoers

RUN curl -O https://bootstrap.pypa.io/get-pip.py
RUN python3.4 get-pip.py

COPY da_server-0.0.1.tar.gz .
RUN pip3.4 install da_server-0.0.1.tar.gz

RUN mkdir /cwd
RUN useradd dev
RUN chown dev:dev /cwd

USER dev
WORKDIR /cwd

CMD ip a && da-server --tcp 0.0.0.0:7776 --client-stoppable
