pipeline {
    agent any
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Install & Test') {
    steps {
        bat '"C:\\Users\\HP 845\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m pip install -r requirements.txt'
        bat '"C:\\Users\\HP 845\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m pytest -q'
    }
}
        stage('Build Docker Image') {
            steps { bat 'docker build -t dailylife-manager:%BUILD_NUMBER% .' }
        }
    }
}