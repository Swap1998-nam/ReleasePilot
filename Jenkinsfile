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
    }

    environment {
        IMAGE_NAME = 'releasepilot'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
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
    }

    post {
        success { echo "ReleasePilot build ${env.BUILD_NUMBER} passed" }
        failure { echo "ReleasePilot build ${env.BUILD_NUMBER} failed" }
        always  { sh 'docker image prune -f || true' }
    }
}
