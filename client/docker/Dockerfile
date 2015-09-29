FROM centos:7

# Install RPMs
RUN yum clean all && yum update -y && yum install -y epel-release && yum clean all
RUN yum install -y python34 && yum clean all

# Install pip
RUN curl -O https://bootstrap.pypa.io/get-pip.py
RUN python3.4 get-pip.py

# Install DA client
COPY da_client-0.0.1.tar.gz .
RUN pip3.4 install da_client-0.0.1.tar.gz

RUN mkdir /cwd
RUN useradd dev
RUN chown dev:dev /cwd

USER dev
WORKDIR /cwd

ENTRYPOINT ["da-cli"]
