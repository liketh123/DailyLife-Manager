pipeline {
    agent any
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Install & Test') {
            steps {
                bat 'python -m pip install -r requirements.txt'
                bat 'pytest -q'
            }
        }
        stage('Build Docker Image') {
            steps { bat 'docker build -t dailylife-manager:%BUILD_NUMBER% .' }
        }
    }
}