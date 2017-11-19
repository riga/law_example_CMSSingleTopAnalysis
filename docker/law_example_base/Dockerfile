FROM centos:7

LABEL name="law_example_base"
LABEL version="0.0.1"

WORKDIR /root/law_example


#
# setup software and environment
#

RUN mkdir /software

# basic environment variables
ENV PATH /usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH
ENV LD_LIBRARY_PATH /usr/local/lib:$LD_LIBRARY_PATH
ENV LIBPATH /usr/local/lib:$LIBPATH
ENV PYTHONPATH /usr/local/lib:/usr/local/lib64/python2.7/site-packages:$PYTHONPATH
ENV PKG_CONFIG_PATH /usr/local/lib/pkgconfig:$PKG_CONFIG_PATH
ENV CMAKE_MODULE_PATH /usr/local/etc/cmake
ENV MANPATH /usr/local/man

# main software
RUN yum -y update; yum clean all
RUN yum -y install yum-plugin-priorities; yum clean all
RUN yum install -y epel-release; yum clean all
RUN yum groupinstall -y "Development Tools"; yum clean all
RUN yum install -y gcc-gfortran openssl-devel pcre-devel mesa-libGL-devel mesa-libGLU-devel \
    glew-devel ftgl-devel fftw-devel cfitsio-devel libxml2-devel libldap-dev libpng-devel \
    avahi-compat-libdns_sd-devel gsl-static gcc-c++ gcc atlas atlas-devel lapack-devel blas-devel \
    curl-devel json-c-devel git make cmake binutils swig nano htop which screen wget python-devel \
    python-pip; yum clean all

# root
RUN cd /software && \
    wget https://root.cern.ch/download/root_v6.10.08.Linux-centos7-x86_64-gcc4.8.tar.gz && \
    tar -xzf root_v6.10.08.Linux-centos7-x86_64-gcc4.8.tar.gz && \
    rm root_v6.10.08.Linux-centos7-x86_64-gcc4.8.tar.gz && \
    echo "source \$ROOTSYS/bin/thisroot.sh" >> /root/.bashrc
ENV ROOTSYS /software/root

# python packages
RUN pip install numpy
RUN pip install scipy
RUN pip install matplotlib
RUN pip install scikit-learn
RUN pip install requests
RUN pip install six
RUN pip install luigi
RUN pip install order
RUN pip install scinum
