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
    steps {
        sh '''
            python3 -m venv .venv
            .venv/bin/python -m pip install --upgrade pip
            .venv/bin/pip install -r requirements.txt
        '''
    }
}

stage('Automated tests') {
    steps {
        sh '''
            .venv/bin/python -m pytest -q
        '''
    }
}
    stage('Build Docker image') {
      steps { sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .' }
    }
    stage('AI risk gate') {
    steps {
        sh '''
            .venv/bin/python -c "
from ml.predict import predict_risk

metrics = {
    'changed_files': 10,
    'test_failures': 0,
    'previous_failures': 0,
    'build_duration': 75,
    'cpu_usage': 45,
    'coverage': 85
}

result = predict_risk(metrics)

print('AI RELEASE RISK ANALYSIS')
print('Risk Score:', result['risk_score'], '%')
print('Risk Level:', result['risk_level'])

for reason in result['reasons']:
    print('-', reason)

if result['risk_score'] >= 70:
    raise SystemExit('RELEASE BLOCKED: High risk detected')
"
        '''
    }
}
    stage('Deploy') {
    steps {
        sh '''
            docker rm -f releasepilot-app || true

            docker run -d \
                --name releasepilot-app \
                --restart unless-stopped \
                -p 5000:5000 \
                releasepilot-demo:${BUILD_NUMBER}
        '''
    }
}
  }
  post {
    failure { echo 'Pipeline failed. Trigger rollback to the previous stable image in your target environment.' }
    always { echo 'Pipeline execution finished.' }
  }
}
