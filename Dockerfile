# Stage 1: Build dependencies
FROM python:3.13-slim-bookworm AS builder

WORKDIR /solutis-sync

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy configuration files for dependency restoration
COPY pyproject.toml uv.lock ./

# Install python dependencies using uv (creates /solutis-sync/.venv)
RUN uv sync --frozen --no-install-project --no-dev


# Stage 2: Final runner image
FROM python:3.13-slim-bookworm AS runner

# Configure environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/solutis-sync/.venv/bin:/opt/mssql-tools17/bin:$PATH" \
    PYTHONPATH="/solutis-sync/src:/solutis-sync" \
    XDG_RUNTIME_DIR="/solutis-sync/src" \
    RUNLEVEL=3 \
    TZ=America/Sao_Paulo \
    LANG=pt_BR.UTF-8 \
    LC_ALL=pt_BR.UTF-8

WORKDIR /solutis-sync

# Install system packages and configure locale & timezone
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -y \
    && apt-get install -y curl locales tzdata \
    && sed -i '/^# pt_BR.UTF-8 UTF-8/s/^# //' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=pt_BR.UTF-8 \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# Install Microsoft SQL Server tools (Do not modify, as requested)
RUN export DEBIAN_FRONTEND=noninteractive \
    && curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc \
    && curl https://packages.microsoft.com/config/debian/11/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update -y \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get install -y unixodbc unixodbc-dev libgssapi-krb5-2

# Cleanup packages to keep the image as small as possible
RUN chmod -R 755 /var \
    && apt-get remove curl -y \
    && apt-get auto-remove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from builder stage
COPY --from=builder /solutis-sync/.venv /solutis-sync/.venv

# Copy application source code
COPY ./src /solutis-sync/src

# Expose port 8003
EXPOSE 8003

# Run application directly using the virtualenv's uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8003", "--workers", "2"]
