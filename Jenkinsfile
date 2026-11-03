pipeline {
  agent any
  environment {
    IMAGE_NAME = 'releasepilot-demo'
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Install dependencies') {
      steps { sh 'python3 -m pip install -r requirements.txt' }
    }
    stage('Automated tests') {
      steps { sh 'python3 -m pytest -q' }
    }
    stage('Build Docker image') {
      steps { sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .' }
    }
    stage('AI risk gate') {
      steps {
        // In the complete demo, call the Flask /api/pipeline/run endpoint here
        // with Jenkins metrics and stop the release when predicted risk >= 70.
        echo 'Connect Jenkins metrics to the ReleasePilot risk API for live gating.'
      }
    }
    stage('Deploy') {
      steps { echo 'Demo deployment stage. Add your target environment credentials and deploy command.' }
    }
  }
  post {
    failure { echo 'Pipeline failed. Trigger rollback to the previous stable image in your target environment.' }
    always { echo 'Pipeline execution finished.' }
  }
}
