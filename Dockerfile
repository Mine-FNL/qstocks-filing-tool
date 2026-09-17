# Production-grade container for the jurisdiction-agnostic filing ingestor.
# Layers are ordered by frequency of change: deps → source → runtime config.
# The browser app image stays slim: no build tools, just the wheel + a tiny
# setup to read .env from a bind mount.
FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    LOG_LEVEL=INFO

# The web app needs no additional system packages beyond what python:slim
# already brings. If you reach for tesseract / onnx-runtime later, install
# them in a separate "*-ocr" target stage so the default image stays small.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first (cached layer). The package is small; pin-free to keep
# the image portable — pip resolves against the same extras declared in
# pyproject.toml under [project] / [project.optional-dependencies].
COPY pyproject.toml ./
COPY requirements*.txt ./
RUN pip install --upgrade pip \
 && pip install .[dev]

# Source + per-stock profiles last so a code change doesn't bust the
# 200 MB pip layer.
COPY qscreen_*.py conftest.py ./
COPY profiles/ ./profiles/
COPY qatar/ ./qatar/
COPY tests/ ./tests/
COPY .env.example ./

# Liveness: a static page makes container health-checks simple. The Flask app's
# /healthz route exposes engine readiness + version for k8s probes.
EXPOSE 8765

# The CLI default-arg seems safest: a tiny web server an operator can curl.
# For one-shot PDF extraction, override the command in compose / k8s.
ENV QSCREEN_APP_HOST=0.0.0.0 QSCREEN_APP_PORT=8765
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${QSCREEN_APP_PORT}/healthz" || exit 1

CMD ["python", "qscreen_app.py"]
