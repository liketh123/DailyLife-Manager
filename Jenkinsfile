pipeline {
    agent any

    environment {
        DOCKER = 'C:\\Users\\HP 845\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        IMAGE = "dailylife-manager:%BUILD_NUMBER%"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"C:\\Users\\HP 845\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat '"C:\\Users\\HP 845\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m pytest -q'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '"%DOCKER%" build -t %IMAGE% .'
            }
        }

        stage('Tag Latest Image') {
            steps {
                bat '"%DOCKER%" tag %IMAGE% dailylife-manager:latest'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                bat 'kubectl apply -f k8s\\deployment.yaml'
                bat 'kubectl apply -f k8s\\service.yaml'
            }
        }

        stage('Verify Deployment') {
            steps {
                bat 'kubectl rollout status deployment/dailylife-manager'
                bat 'kubectl get pods'
                bat 'kubectl get services'
            }
        }
    }
}