pipeline {
    agent any

    environment {
        JENKINS_MODE = "1"          // Limiter à quelques villes pour tests
        SPARK_HOME = "/opt/spark"   // Chemin Spark dans le conteneur
        PATH = "$SPARK_HOME/bin:$PATH"
        VENV_PATH = "/opt/venv/bin" // chemin du virtualenv contenant papermill
    }

    stages {
        stage('Checkout Jenkinsfile') {
            steps {
                git branch: 'jenkins-pipeline', url: 'https://github.com/12halima/Transport_Recommander/', credentialsId: 'githubPath'
            }
        }

        stage('Fetch Script from Main') {
            steps {
                sh 'git fetch origin main'
                sh 'git checkout origin/main -- Process_GTFS-OSM/Network_Base.ipynb'
            }
        }

        stage('Run Notebook with Papermill') {
            steps {
                // On utilise papermill depuis le venv pour exécuter le notebook
                sh '''
                $VENV_PATH/papermill Process_GTFS-OSM/Network_Base.ipynb Process_GTFS-OSM/Network_Base_output.ipynb
                '''
            }
        }
    }
}
