FROM texlive/texlive:latest

# labels
LABEL AUTHOR='Luc Laurent'
LABEL MAINTAINER='Luc Laurent & Benoit Nennig'

# install debian packages
RUN apt update && \
    apt install -yy wget ghostscript imagemagick libtext-unidecode-perl latexml xmlindent python3-pip git && \
    apt clean

# move policy file
RUN mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.off

# install pip and Python pkgs
# RUN pip3 install -U pip && \
#     pip install amc2moodle
WORKDIR /tmp
RUN git clone https://github.com/nennigb/amc2moodle.git -b master
WORKDIR /tmp/amc2moodle
RUN pip3 install .

# check if amc2moodle and moodle2amc work
WORKDIR /
RUN python -m amc2moodle.amc2moodle.test && \
    python -m amc2moodle.utils.test

# create dir
RUN mkdir /tmp/work
RUN mkdir /tmp/daemon
VOLUME /tmp/work
VOLUME /tmp/daemon

# create new user
RUN groupadd -r user && useradd -r -g user user
RUN chown user:user /tmp/daemon
RUN chown user:user /tmp/work


USER user

#working dir
WORKDIR /tmp/work

#declare directory using environement 
ENV MONITOR_DIR=/tmp/work
ENV LOG_DIR=/tmp/daemon

# copy autorun script for amc2moodle/moodle2amc
COPY autorun-amc2moodle.sh /tmp/.
#RUN ["/tmp/autorun-amc2moodle.sh",">","/dev/null","2>&1&"]

# execute script
ENTRYPOINT ["/tmp/autorun-amc2moodle.sh",">","/dev/null","2>&1&"]
# ENTRYPOINT ["tail","-f","/dev/null"]