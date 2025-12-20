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
        stage('Setup Python env') {
            steps {
                sh '''
                    python3 --version

                    if [ ! -d "$VENV_DIR" ]; then
                        python3 -m venv $VENV_DIR
                    fi

                    . $VENV_DIR/bin/activate
                    pip install --upgrade pip
                    pip install pandas papermill
                '''
            }
        }
        stage('Run CI Notebook with Papermill') {
            steps {
                sh '''
                    # Activer le virtualenv
                    . .venv_ci/bin/activate
        
                    # Installer ipykernel au cas où
                    python3 -m pip install --upgrade pip
                    python3 -m pip install ipykernel papermill pandas
        
                    # Option 1 : utiliser le kernel par défaut du venv
                    python3 -m papermill \
                        Jenkins/ci_network_processing.ipynb \
                        Jenkins/ci_network_processing_output.ipynb
        
                    # Désactiver le venv après exécution
                    deactivate
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
