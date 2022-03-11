FROM texlive/texlive:latest

# labels
LABEL  AUTHOR='Luc Laurent'
LABEL MAINTAINER='Luc Laurent & Benoit Nennig'

# install debian packages
RUN apt update && \
    apt install -yy wget ghostscript imagemagick libtext-unidecode-perl latexml xmlindent python3-pip && \
    apt clean

# move policy file
RUN mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.off

# install pip and Python pkgs
RUN pip3 install -U pip && \
    pip install amc2moodle

# check if amc2moodle and moodle2amc work
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
run chown user:user /tmp/work


USER user

#working dir
WORKDIR /tmp/work

# copy autorun script for amc2moodle/moodle2amc
COPY autorun-amc2moodle.sh /tmp/.

# execute script
ENTRYPOINT ["/tmp/autorun-amc2moodle.sh",">","/dev/null","2>&1"]