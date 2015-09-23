FROM centos:7

RUN yum clean all && yum update -y && yum install -y sudo epel-release && yum clean all
RUN yum install -y python34 python3-pip && yum clean all

# Sudo complains about not having TTY unless this is done (see rhbz#1020147)
RUN echo 'Defaults !requiretty' >> /etc/sudoers

RUN mkdir /cwd /devassistant-home

ADD server-wrapper.sh .

ENTRYPOINT ["./server-wrapper.sh"]
