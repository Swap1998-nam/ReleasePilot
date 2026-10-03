pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    parameters {
        booleanParam(name: 'RUN_SONAR', defaultValue: false, description: 'Run SonarQube analysis + quality gate')
        booleanParam(name: 'RUN_TRIVY', defaultValue: false, description: 'Scan Docker image with Trivy')
        booleanParam(name: 'RUN_DEPLOY', defaultValue: true, description: 'Deploy container on this host')
    }

    environment {
        IMAGE_NAME = 'releasepilot'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
        APP_NAME   = 'releasepilot'
        APP_PORT   = '8081'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'python3 --version && docker --version'
            }
        }

        stage('SonarQube Analysis') {
            when { expression { params.RUN_SONAR } }
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                              -Dsonar.projectKey=ReleasePilot \
                              -Dsonar.projectName=ReleasePilot \
                              -Dsonar.sources=. \
                              -Dsonar.exclusions=tests/**,**/__pycache__/** \
                              -Dsonar.python.version=3 \
                              -Dsonar.javascript.node.maxspace=512
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            when { expression { params.RUN_SONAR } }
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        stage('Trivy Scan') {
            when { expression { params.RUN_TRIVY } }
            steps {
                sh '''
                    trivy image --no-progress --ignore-unfixed \
                      --severity HIGH,CRITICAL --exit-code 1 \
                      ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }

        stage('Deploy') {
            when { expression { params.RUN_DEPLOY } }
            steps {
                sh '''
                    PREV_IMAGE=$(docker inspect -f '{{.Config.Image}}' ${APP_NAME} 2>/dev/null || true)
                    docker rm -f ${APP_NAME} 2>/dev/null || true

                    docker run -d --name ${APP_NAME} --restart unless-stopped \
                      -p ${APP_PORT}:8081 ${IMAGE_NAME}:${IMAGE_TAG}

                    for i in $(seq 1 15); do
                        if curl -fsS http://localhost:${APP_PORT}/health/ready >/dev/null; then
                            echo "Deployed ${IMAGE_NAME}:${IMAGE_TAG} -> healthy"
                            exit 0
                        fi
                        sleep 2
                    done

                    echo "Health check failed, rolling back"
                    docker logs --tail 30 ${APP_NAME} || true
                    docker rm -f ${APP_NAME} || true
                    if [ -n "$PREV_IMAGE" ]; then
                        docker run -d --name ${APP_NAME} --restart unless-stopped \
                          -p ${APP_PORT}:8081 "$PREV_IMAGE"
                        echo "Rolled back to $PREV_IMAGE"
                    fi
                    exit 1
                '''
            }
        }
    }

    post {
        success { echo "ReleasePilot build ${env.BUILD_NUMBER} passed" }
        failure { echo "ReleasePilot build ${env.BUILD_NUMBER} failed" }
        always  { sh 'docker image prune -f || true' }
    }
}
