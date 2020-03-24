FROM centos:7

ENV CPU_CORE 4

# Activate systemd. Taken from https://hub.docker.com/_/centos
ENV container docker
RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == \
systemd-tmpfiles-setup.service ] || rm -f $i; done); \
rm -f /lib/systemd/system/multi-user.target.wants/*;\
rm -f /etc/systemd/system/*.wants/*;\
rm -f /lib/systemd/system/local-fs.target.wants/*; \
rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -f /lib/systemd/system/basic.target.wants/*;\
rm -f /lib/systemd/system/anaconda.target.wants/*;
VOLUME [ "/sys/fs/cgroup" ]

RUN yum update -y
RUN yum groupinstall -y "Development Tools" "System Tools"
RUN yum install -y \
    git bzip2 wget subversion which sox \
    gcc-c++ make automake autoconf zlib-devel atlas-static \
     python python3-devel cmake tcsh pcre-devel
RUN yum remove -y swig
RUN yum install -y http://mirror.centos.org/centos/7/extras/x86_64/Packages/swig3-3.0.12-17.el7.x86_64.rpm

# install cuda
RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm dkms
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/cuda-repo-rhel7-10.0.130-1.x86_64.rpm
RUN rpm -i cuda-repo-*.rpm
RUN yum install -y cuda

WORKDIR /usr/local/
# Use the newest idlak version
#RUN git clone https://github.com/Idlak/idlak.git
RUN git clone https://github.com/skaiste/idlak.git
WORKDIR /usr/local/idlak
RUN git checkout server-docker
RUN git pull

WORKDIR /usr/local/idlak/tools
RUN mkdir python
RUN touch python/.use_default_python
RUN extras/check_dependencies.sh
RUN make -j $CPU_CORE
RUN ./install_idlak.sh

WORKDIR /usr/local/idlak/src
ENV SWIG=/usr/bin/swig
#RUN ../tools/install_idlak.sh
RUN ./configure --shared --cudatk-dir=/usr/local/cuda-10.2/
RUN make clean
RUN make depend -j $CPU_CORE
RUN make -j $CPU_CORE
RUN make ext -j $CPU_CORE

WORKDIR /usr/local/idlak/idlak-server
RUN python3 -m pip install -r requirements.txt
#RUN python3 runserver.py
#CMD ["python3", "runserver.py"]

EXPOSE 80

# setup nginx
RUN yum install -y nginx

# setup idlak service
RUN cp /usr/local/idlak/idlak-misc/docker/centos/wsgi.ini ./.
RUN cp /usr/local/idlak/idlak-misc/docker/centos/idlak.service /etc/systemd/system/.
RUN cp /usr/local/idlak/idlak-misc/docker/centos/idlak.conf /etc/nginx/conf.d/idlak.conf
RUN systemctl start idlak
RUN systemctl enable idlak

# continue setting up nginx
RUN usermod -a -G root nginx
RUN chmod 710 /usr/local/idlak
RUN systemctl start nginx
RUN systemctl enable nginx

CMD ["/usr/sbin/init"]

