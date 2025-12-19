pipeline {
    agent any

    environment {
        JENKINS_MODE = "1"
        SPARK_HOME   = "/opt/spark"
        PATH         = "/opt/venv/bin:${SPARK_HOME}/bin:${PATH}"
        PYSPARK_PYTHON = "/opt/venv/bin/python"
        PYSPARK_DRIVER_PYTHON = "/opt/venv/bin/python"
    }

    stages {

        stage('Checkout Jenkinsfile') {
            steps {
                git branch: 'jenkins-pipeline',
                    url: 'https://github.com/12halima/Transport_Recommander/',
                    credentialsId: 'githubPath'
            }
        }

        stage('Fetch Notebook from Main') {
            steps {
                sh '''
                    git fetch origin main
                    git checkout origin/main -- Process_GTFS-OSM/Network_Base.ipynb
                '''
            }
        }

        stage('Run Notebook with Papermill') {
            steps {
                sh '''
                    papermill \
                      Process_GTFS-OSM/Network_Base.ipynb \
                      Process_GTFS-OSM/Network_Base_output.ipynb \
                      -p JENKINS_MODE 1 \
                      --kernel python3
                '''
            }
        }

        stage('Archive Output Notebook') {
            steps {
                archiveArtifacts artifacts: 'Process_GTFS-OSM/*_output.ipynb',
                                 fingerprint: true
            }
        }
    }

    post {
        failure {
            echo "Pipeline échoué. Le notebook a crashé, pas Jenkins."
        }
        success {
            echo "Notebook exécuté avec succès. Jenkins peut respirer."
        }
    }
}
