FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl python3 python3-pip python3-venv \
    libgtk-3-0 libx11-6 libxext6 libxrender1 libxtst6 libxi6 libxrandr2 \
    libxinerama1 libxcursor1 libasound2t64 libfreetype6 fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Audiveris 5.11.0 Linux installer includes its own Java runtime.
ARG AUDIVERIS_VERSION=5.11.0
RUN curl -fL "https://github.com/Audiveris/audiveris/releases/download/${AUDIVERIS_VERSION}/Audiveris-${AUDIVERIS_VERSION}-ubuntu24.04-x86_64.deb" \
      -o /tmp/audiveris.deb \
    && apt-get update \
    && apt-get install -y /tmp/audiveris.deb \
    && rm -f /tmp/audiveris.deb \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /opt/audiveris/bin/Audiveris /usr/local/bin/audiveris

WORKDIR /app
COPY requirements.txt .
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
ENV PATH="/opt/venv/bin:${PATH}"
COPY . .

ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
