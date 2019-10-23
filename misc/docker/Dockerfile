FROM python:3.7-stretch

RUN apt-get -qq update \
 && apt-get install -y -qq --no-install-recommends \
    git curl unzip build-essential ca-certificates ttfautohint \
 && pip install virtualenv

RUN mkdir /inter
WORKDIR /inter

COPY . /inter/
RUN rm Dockerfile

RUN ln -s /host/src src \
 && ln -s /host/misc misc \
 && ln -s /host/version.txt . \
 && ln -s /host/githash.txt . \
 && ln -s /host/Makefile . \
 && ./init.sh \
 && rm -rf build/fonts \
 && mkdir -p /host/build/fonts \
 && ln -s /host/build/fonts build/fonts

RUN rm init.sh && ln -s /host/init.sh . \
 && echo "source /inter/init.sh" >> "$HOME/.bashrc" \
 && echo "alias l='ls -lAF'" >> "$HOME/.bashrc" \
 && echo 'export PS1="\[\e[33;1m\]\u@\w\[\e[0m\]\\\$ "' >> "$HOME/.bashrc"

# cleanup
RUN apt-get -y autoremove \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENV PATH=/inter/build/venv/bin:$PATH

VOLUME /host

CMD "/bin/bash"
