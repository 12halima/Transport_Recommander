pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = "1"
        VENV_DIR = ".venv_ci"
        NOTEBOOK = "Jenkins/ci_network_processing.ipynb"
        OUTPUT_DIR = "Jenkins/output"
        OUTPUT_NOTEBOOK = "${OUTPUT_DIR}/ci_network_processing_output.ipynb"
    }

    stages {
        stage('Checkout Repo') {
            steps {
                // Clone complet du repo sur la branche principale
                git branch: 'main',
                    url: 'https://github.com/12halima/Transport_Recommander/',
                    credentialsId: 'githubPath'
            }
        }

        stage('Setup Python env') {
            steps {
                sh '''
                    python3 --version
                    # Créer le venv si n'existe pas
                    if [ ! -d "$VENV_DIR" ]; then
                        python3 -m venv $VENV_DIR
                    fi
                    # Activer venv et installer dépendances
                    . $VENV_DIR/bin/activate
                    pip install --upgrade pip
                    pip install papermill pandas ipykernel
                '''
            }
        }

        stage('Run CI Notebook with Papermill') {
            steps {
                sh '''
                    # Activer le virtualenv
                    . $VENV_DIR/bin/activate
                    # Créer le dossier output si absent
                    mkdir -p $OUTPUT_DIR
                    # Exécuter le notebook avec Papermill
                    python3 -m papermill $NOTEBOOK $OUTPUT_NOTEBOOK
                '''
            }
        }

        stage('Archive Output Notebook') {
            steps {
                archiveArtifacts artifacts: "${OUTPUT_DIR}/*_output.ipynb",
                                 fingerprint: true
            }
        }
    }

    post {
        failure {
            echo "Pipeline échoué. Vérifie les logs."
        }
        success {
            echo "Pipeline réussi. Notebook exécuté et archivé."
        }
    }
}
