pipeline {
    agent any

    environment {
        JENKINS_MODE = "1"          // Limiter à quelques villes pour tests
        SPARK_HOME = "/opt/spark"   // Chemin Spark dans le conteneur
        PATH = "$SPARK_HOME/bin:$PATH"
    }

    stages {
        stage('Checkout Jenkinsfile') {
            steps {
                // On récupère uniquement la branche du Jenkinsfile
                git branch: 'jenkins-pipeline', url: 'https://github.com/12halima/Transport_Recommander/', credentialsId: 'githubPath'
            }
        }

        stage('Fetch Script from Main') {
            steps {
                // On prend le script depuis la branche main sans changer de branche entière
                sh 'git fetch origin main'
                sh 'git checkout origin/main -- Process_GTFS-OSM/Network_Base.ipynb'
            }
        }

        stage('Run PySpark Script') {
            steps {
                sh 'spark-submit Process_GTFS-OSM/Network_Base.ipynb'
            }
        }
    }
}
