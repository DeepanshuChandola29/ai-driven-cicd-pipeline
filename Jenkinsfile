
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'releasepilot-demo'
        CONTAINER_NAME = 'releasepilot-app'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
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
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .
                '''
            }
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
                    NEW_IMAGE="${IMAGE_NAME}:${BUILD_NUMBER}"

                    # Get currently running image
                    PREVIOUS_IMAGE=$(docker inspect \
                        --format='{{.Config.Image}}' \
                        ${CONTAINER_NAME} 2>/dev/null || true)

                    echo "Previous image: ${PREVIOUS_IMAGE}"
                    echo "New image: ${NEW_IMAGE}"

                    # Remove old container
                    docker rm -f ${CONTAINER_NAME} || true

                    # Deploy new container
                    if ! docker run -d \
                        --name ${CONTAINER_NAME} \
                        --restart unless-stopped \
                        -p 5000:5000 \
                        "$NEW_IMAGE"; then

                        echo "Deployment failed!"

                        if [ -n "$PREVIOUS_IMAGE" ]; then
                            echo "Restoring previous image..."

                            docker run -d \
                                --name ${CONTAINER_NAME} \
                                --restart unless-stopped \
                                -p 5000:5000 \
                                "$PREVIOUS_IMAGE"
                        fi

                        exit 1
                    fi

                    # Application health check
                    HEALTHY=0

                    for i in $(seq 1 10); do
                        echo "Health check attempt $i of 10"

                        if docker exec ${CONTAINER_NAME} \
                            python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/', timeout=5)" \
                            2>/dev/null; then

                            HEALTHY=1
                            break
                        fi

                        sleep 3
                    done

                    # Rollback if health check fails
                    if [ "$HEALTHY" -eq 0 ]; then

                        echo "Health check failed!"

                        docker logs --tail 30 ${CONTAINER_NAME} || true
                        docker rm -f ${CONTAINER_NAME} || true

                        if [ -n "$PREVIOUS_IMAGE" ]; then

                            echo "Rolling back to: $PREVIOUS_IMAGE"

                            docker run -d \
                                --name ${CONTAINER_NAME} \
                                --restart unless-stopped \
                                -p 5000:5000 \
                                "$PREVIOUS_IMAGE"

                            echo "Previous version restored."

                        else
                            echo "No previous version available!"
                        fi

                        exit 1
                    fi

                    echo "Deployment successful!"
                    echo "Application is healthy."
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check the console output for details.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}
