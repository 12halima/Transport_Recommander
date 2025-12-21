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
                if [ ! -d "$VENV_DIR" ]; then
                    python3 -m venv $VENV_DIR
                fi
                . $VENV_DIR/bin/activate
                pip install --upgrade pip
                pip install papermill pandas ipykernel
                '''
            }
        }

        stage('Run CI data generation') {
            steps {
                sh '''
                . $VENV_DIR/bin/activate
                mkdir -p $OUTPUT_DIR
                python -m papermill \
                  Jenkins/ci_network_processing.ipynb \
                  $OUTPUT_DIR/ci_network_processing_output.ipynb
                '''
            }
        }

        stage('Run CI data tests (pandas)') {
            steps {
                sh '''
                . $VENV_DIR/bin/activate
                mkdir -p $OUTPUT_DIR
                python -m papermill \
                  Jenkins/ci_edges_tests.ipynb \
                  $OUTPUT_DIR/ci_edges_tests_output.ipynb
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'Jenkins/output/*.ipynb', fingerprint: true
        }
        success {
            echo "✅ CI DATA VALIDÉE – logique métier OK"
        }
        failure {
            echo "❌ CI DATA ÉCHOUÉE – assertions cassées"
        }
    }
}
