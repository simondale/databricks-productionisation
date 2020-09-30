FROM ubuntu:18.04

RUN apt-get update -qq \
 && apt-get install -qq -y python3 wget \
 && wget -O ~/miniconda3.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
 && bash ~/miniconda3.sh -b -u -p \
 && rm -rf ~/miniconda3.sh

WORKDIR /model

COPY conda.yml .
COPY setup.py .
COPY src/iris_model ./src/iris_model
COPY scripts/server.sh .

RUN eval "$(~/miniconda3/bin/conda shell.bash hook)" \
 && conda env create --force --quiet --name hosting --file conda.yml \
 && conda activate hosting \
 && python setup.py develop

EXPOSE 5000

CMD ["/bin/bash", "/model/server.sh"]



