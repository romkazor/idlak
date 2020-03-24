FROM centos:7

ENV CPU_CORE 4

RUN yum update -y
RUN yum groupinstall -y "Development Tools" "System Tools"
RUN yum install -y \
    git bzip2 wget subversion which sox \
    gcc-c++ make automake autoconf zlib-devel atlas-static \
     python python3-devel cmake tcsh pcre-devel nginx
RUN yum remove -y swig
RUN yum install -y http://mirror.centos.org/centos/7/extras/x86_64/Packages/swig3-3.0.12-17.el7.x86_64.rpm

# install cuda
RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm dkms
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/cuda-repo-rhel7-10.0.130-1.x86_64.rpm
RUN rpm -i cuda-repo-*.rpm
RUN yum install -y cuda

WORKDIR /usr/local/
# Use the newest idlak version
RUN git clone https://github.com/Idlak/idlak.git

WORKDIR /usr/local/idlak/tools
RUN mkdir python
RUN touch python/.use_default_python
RUN extras/check_dependencies.sh
RUN make -j $CPU_CORE
RUN ./install_idlak.sh

WORKDIR /usr/local/idlak/src
ENV SWIG=/usr/bin/swig
#RUN ../tools/install_idlak.sh hmm
RUN ./configure --shared --cudatk-dir=/usr/local/cuda-10.2/
RUN make clean
RUN make depend -j $CPU_CORE
RUN make -j $CPU_CORE
RUN make ext -j $CPU_CORE

WORKDIR /usr/local/idlak/idlak-server
RUN python3 -m pip install -r requirements.txt
#RUN python3 runserver.py

