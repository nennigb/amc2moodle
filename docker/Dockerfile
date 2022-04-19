FROM texlive/texlive:latest

# labels
LABEL AUTHOR='Luc Laurent'
LABEL MAINTAINER='Luc Laurent & Benoit Nennig'
LABEL org.opencontainers.image.source = "https://github.com/nennigb/amc2moodle/"

# declare useful directories using environement 
ENV MONITOR_DIR=/tmp/work
ENV LOG_DIR=/tmp/daemon
ENV INSTALL_DIR_A2M=/tmp/amc2moodle

# install debian packages
RUN apt update && \
    apt install -yy wget ghostscript imagemagick libtext-unidecode-perl latexml xmlindent python3-pip git && \
    apt clean

# move policy file
RUN mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.off

# install pip and Python pkg
# RUN pip3 install -U pip && \
#     pip install amc2moodle
WORKDIR /tmp
RUN git clone https://github.com/nennigb/amc2moodle.git -b master ${INSTALL_DIR_A2M}
WORKDIR ${INSTALL_DIR_A2M}
RUN pip3 install -U pip && \
    pip3 install .

# check if amc2moodle and moodle2amc work
WORKDIR /
ENV TEXINPUTS=.:${INSTALL_DIR_A2M}/amc2moodle/moodle2amc/test:$TEXINPUTS
RUN echo ${TEXINPUTS}
RUN python -m amc2moodle.amc2moodle.test && \
    python -m amc2moodle.utils.test && \
    python -m amc2moodle.moodle2amc.test



# create dir
RUN mkdir ${MONITOR_DIR} && \
    mkdir ${LOG_DIR}
VOLUME ${MONITOR_DIR}
VOLUME ${LOG_DIR}

# create new user
RUN groupadd -r user && \
    useradd -r -g user user && \
    chown user:user ${MONITOR_DIR} && \
    chown user:user ${LOG_DIR}

# switch to "user"
USER user

# working dir
WORKDIR ${MONITOR_DIR}

# copy autorun script for amc2moodle/moodle2amc
COPY autorun-amc2moodle.sh /tmp/.
#RUN ["/tmp/autorun-amc2moodle.sh",">","/dev/null","2>&1&"]

# execute script
ENTRYPOINT ["/tmp/autorun-amc2moodle.sh",">","/dev/null","2>&1&"]
# ENTRYPOINT ["tail","-f","/dev/null"]
