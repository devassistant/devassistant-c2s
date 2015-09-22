FROM fedora:22

RUN dnf clean all && dnf install -y sudo && dnf clean all

RUN echo -e '#!/usr/bin/bash\ngroupadd dev -g $DEV_GID\nuseradd dev -u $DEV_UID -g $DEV_GID\nsudo -u dev touch /tmp/a' > /root/da-server && chmod +x /root/da-server

ENTRYPOINT ["/root/da-server"]
