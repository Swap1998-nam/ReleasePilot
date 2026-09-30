# ReleasePilot

A database-free release readiness dashboard for DevOps and DevSecOps practice. Inputs are simulations; the dashboard does not itself scan images or run tests. No packages to install.

## Locally

Python 3.10+: `python3 app.py` then open http://localhost:8080. Run tests with `python3 -m unittest discover -s tests -v`.

## Docker

`docker build -t releasepilot:local .`

`docker run --rm -p 8080:8080 releasepilot:local`

## API

GET `/health/live`, `/health/ready`, `/metrics`; POST `/api/assess` with the seven fields shown in the UI. Nothing is persisted.

## Jenkins and SonarQube

Create a Pipeline from SCM. Agent needs Python 3 and Docker. To enable Sonar analysis set `RUN_SONAR=true`, configure Jenkins SonarQube server named `SonarQube`, install SonarScanner and the Jenkins SonarQube plugin, and point the SonarQube webhook to `https://YOUR-JENKINS/sonarqube-webhook/`. To enable image scanning install Trivy and set `RUN_TRIVY=true`. Optional stages are off by default. Next exercises: push image to ECR, deploy to EKS with health probes, scrape metrics with Prometheus, add Grafana dashboard, and sign image with Cosign.
