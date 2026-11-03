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
            NEW_IMAGE="releasepilot-demo:${BUILD_NUMBER}"

            # Save the currently running version
            PREVIOUS_IMAGE=$(docker inspect --format='{{.Config.Image}}' releasepilot-app 2>/dev/null || true)

            echo "Previous image: ${PREVIOUS_IMAGE}"
            echo "Deploying new image: ${NEW_IMAGE}"

            # Stop the old container
            docker rm -f releasepilot-app || true

            # Start the new version
            if ! docker run -d \
                --name releasepilot-app \
                --restart unless-stopped \
                -p 5000:5000 \
                "$NEW_IMAGE"; then

                echo "New deployment failed!"

                if [ -n "$PREVIOUS_IMAGE" ]; then
                    echo "Restoring previous version..."
                    docker run -d \
                        --name releasepilot-app \
                        --restart unless-stopped \
                        -p 5000:5000 \
                        "$PREVIOUS_IMAGE"
                fi

                exit 1
            fi

            # Check application health (up to 10 attempts)
            HEALTHY=0

            for i in $(seq 1 10); do
                echo "Health check attempt $i of 10..."

                if docker exec releasepilot-app python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/', timeout=5)" 2>/dev/null; then
                    HEALTHY=1
                    break
                fi

                sleep 3
            done

            # Rollback if health check fails
            if [ "$HEALTHY" -eq 0 ]; then
                echo "Health check failed! Starting rollback..."

                docker logs --tail 30 releasepilot-app || true
                docker rm -f releasepilot-app || true

                if [ -n "$PREVIOUS_IMAGE" ]; then
                    echo "Restoring previous image: $PREVIOUS_IMAGE"

                    docker run -d \
                        --name releasepilot-app \
                        --restart unless-stopped \
                        -p 5000:5000 \
                        "$PREVIOUS_IMAGE"

                    echo "Previous version restored."
                else
                    echo "No previous version available!"
                fi

                exit 1
            fi

            echo "Deployment successful! Application is healthy."
        '''
    }
}

}
  }
  post {
    failure { echo 'Pipeline failed. Trigger rollback to the previous stable image in your target environment.' }
    always { echo 'Pipeline execution finished.' }
  }
}
