pipeline {
  agent any
  stages {
    stage('Test') { steps { sh 'python3 -m unittest discover -s tests -v' } }
    stage('SonarQube') {
      when { expression { env.RUN_SONAR == 'true' } }
      steps { withSonarQubeEnv('SonarQube') {
        sh 'sonar-scanner -Dsonar.projectKey=releasepilot -Dsonar.sources=app.py,index.html -Dsonar.tests=tests'
      } }
    }
    stage('Quality Gate') {
      when { expression { env.RUN_SONAR == 'true' } }
      steps { timeout(time: 5, unit: 'MINUTES') { waitForQualityGate abortPipeline: true } }
    }
    stage('Build') { steps { sh 'docker build -t releasepilot:$BUILD_NUMBER .' } }
    stage('Scan') {
      when { expression { env.RUN_TRIVY == 'true' } }
      steps { sh 'trivy image --exit-code 1 --severity HIGH,CRITICAL releasepilot:$BUILD_NUMBER' }
    }
  }
}
