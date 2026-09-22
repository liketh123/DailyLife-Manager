pipeline {
    agent any

    environment {

        // Python
        PYTHON = 'C:\\Users\\HP 845\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'

        // Docker
        DOCKER = 'C:\\Users\\HP 845\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'

        // CHANGE THIS IF "where.exe kubectl" SHOWS A DIFFERENT PATH
        KUBECTL = 'C:\\Users\\HP 845\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\kubectl.exe'

        // Kubernetes configuration
        KUBECONFIG = 'C:\\Users\\HP 845\\.kube\\config'

        // Docker image name
        IMAGE_NAME = 'dailylife-manager'
    }

    stages {

        stage('Checkout') {
            steps {
                echo '===== CHECKOUT STAGE ====='

                checkout scm

                bat 'echo Jenkins Workspace: %WORKSPACE%'
                bat 'dir "%WORKSPACE%"'
            }
        }


        stage('Check Tools') {
            steps {
                echo '===== CHECKING TOOLS ====='

                bat '"%PYTHON%" --version'

                bat '"%DOCKER%" --version'

                bat '"%KUBECTL%" version --client'

                bat '"%KUBECTL%" config current-context'
            }
        }


        stage('Install Dependencies') {
            steps {
                echo '===== INSTALLING PYTHON DEPENDENCIES ====='

                bat '"%PYTHON%" -m pip install -r "%WORKSPACE%\\requirements.txt"'
            }
        }


        stage('Run Tests') {
            steps {
                echo '===== RUNNING AUTOMATED TESTS ====='

                bat '"%PYTHON%" -m pytest -q "%WORKSPACE%\\tests"'
            }
        }


        stage('Build Docker Image') {
            steps {
                echo '===== BUILDING DOCKER IMAGE ====='

                bat '"%DOCKER%" build -t %IMAGE_NAME%:%BUILD_NUMBER% "%WORKSPACE%"'
            }
        }


        stage('Tag Docker Image') {
            steps {
                echo '===== TAGGING DOCKER IMAGE ====='

                bat '"%DOCKER%" tag %IMAGE_NAME%:%BUILD_NUMBER% %IMAGE_NAME%:latest'

                bat '"%DOCKER%" images %IMAGE_NAME%'
            }
        }


        stage('Check Kubernetes') {
            steps {
                echo '===== CHECKING KUBERNETES ====='

                bat '"%KUBECTL%" config get-contexts'

                bat '"%KUBECTL%" config use-context docker-desktop'

                bat '"%KUBECTL%" get nodes'
            }
        }


        stage('Deploy to Kubernetes') {
            steps {
                echo '===== DEPLOYING TO KUBERNETES ====='

                bat '"%KUBECTL%" apply -f "%WORKSPACE%\\k8s\\deployment.yaml"'

                bat '"%KUBECTL%" apply -f "%WORKSPACE%\\k8s\\service.yaml"'
            }
        }


        stage('Wait for Deployment') {
            steps {
                echo '===== WAITING FOR KUBERNETES DEPLOYMENT ====='

                bat '"%KUBECTL%" rollout status deployment/dailylife-manager --timeout=120s'
            }
        }


        stage('Verify Pods') {
            steps {
                echo '===== VERIFYING PODS ====='

                bat '"%KUBECTL%" get pods -o wide'

                bat '"%KUBECTL%" get deployments'

                bat '"%KUBECTL%" get services'
            }
        }


        stage('Verify Application') {
            steps {
                echo '===== VERIFYING APPLICATION ====='

                bat '"%KUBECTL%" get pods'

                bat '"%KUBECTL%" get service dailylife-service'
            }
        }
    }


    post {

        success {
            echo '=========================================='
            echo 'CI/CD PIPELINE COMPLETED SUCCESSFULLY'
            echo '=========================================='
        }

        failure {
            echo '=========================================='
            echo 'CI/CD PIPELINE FAILED'
            echo 'CHECK THE CONSOLE OUTPUT ABOVE'
            echo '=========================================='
        }

        always {
            echo 'Jenkins Workspace: %WORKSPACE%'
        }
    }
}