FROM python:3.12-slim
WORKDIR /app
COPY --chown=10001:10001 app.py index.html ./
USER 10001:10001
EXPOSE 8080
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health/ready', timeout=2)"
CMD ["python", "app.py"]
