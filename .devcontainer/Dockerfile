FROM ubuntu:latest

ARG USER=developer
ARG DEBIAN_FRONTEND=noninteractive
RUN apt update \
    && apt install -y --no-install-recommends sudo git zsh curl wget ca-certificates \
    && apt clean \
    && apt autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /usr/bin/zsh ${USER} \
    && echo "${USER} ALL=(ALL) NOPASSWD: ALL" >/etc/sudoers.d/${USER} \
    && chmod 0440 /etc/sudoers.d/${USER}


USER ${USER}
ARG HOME=/home/${USER}
WORKDIR ${HOME}

ENV UV_SYSTEM_PYTHON=1
ENV UV_PROJECT_ENVIRONMENT=system
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

