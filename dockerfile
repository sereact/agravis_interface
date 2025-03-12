#SIMPLE DOCKERFILE FOR A PYTHON APPLICATION
FROM python:3.10-bullseye
LABEL maintainer="sereact"
ENV DEBIAN_FRONTEND=noninteractive

# COPY THE WHEEL FILE TO THE CONTAINER
COPY ./wheelhouse /wheelhouse
RUN pip install /wheelhouse/*

COPY ./run_services /run_services

#change the permissions of the folders to allow the user to read and write the python and json files (from the activeants_interface folder)
RUN chmod -R 755 /run_services
RUN chmod -R 755 /wheelhouse

ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID usergroup && \
    useradd -m -u $UID -g $GID -s /bin/bash user

USER user

