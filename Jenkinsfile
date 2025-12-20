pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = "1"
        VENV_DIR = ".venv_ci"
    }

    stages {

        stage('Checkout Jenkinsfile') {
            steps {
                git branch: 'jenkins-pipeline',
                    url: 'https://github.com/12halima/Transport_Recommander/',
                    credentialsId: 'githubPath'
            }
        }

        stage('Fetch CI Notebook from Main') {
            steps {
                sh '''
                    git fetch origin main
                    git checkout origin/main -- Jenkins/ci_network_processing.ipynb
                '''
            }
        }

        stage('Run CI Notebook with Papermill') {
            steps {
                sh '''
                    . $VENV_DIR/bin/activate

                    papermill \
                      Jenkins/ci_network_processing.ipynb \
                      Jenkins/ci_network_processing_output.ipynb \
                      --kernel python3
                '''
            }
        }

        stage('Archive Output Notebook') {
            steps {
                archiveArtifacts artifacts: 'Jenkins/*_output.ipynb',
                                 fingerprint: true
            }
        }
    }

    post {
        failure {
            echo "Pipeline échoué. La logique CI est fausse, Jenkins va bien."
        }
        success {
            echo "CI validée. Logique métier OK, prod peut dormir."
        }
    }
}
