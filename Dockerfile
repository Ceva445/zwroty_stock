FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# LibreOffice — для конвертації xlsx -> pdf (wz_generator.convert_xlsx_to_pdf);
# fonts-liberation/dejavu — коректний рендер польських діакритиків у PDF.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libreoffice-calc \
        fonts-liberation \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app /entrypoint.sh

USER appuser

EXPOSE 8000

CMD ["/entrypoint.sh"]
