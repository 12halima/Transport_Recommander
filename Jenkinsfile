pipeline {
    agent {
        docker {
            // Image Docker avec Spark et Hadoop
            image 'bitnami/spark:latest'
            args '-v /var/jenkins_home:/var/jenkins_home'
        }
    }

    environment {
        JENKINS_MODE = "1"  // active le mode échantillon pour limiter à 5 villes
    }

    stages {
        stage('Checkout Jenkins Branch') {
            steps {
                git branch: 'jenkins-pipeline', 
                    url: 'https://github.com/12halima/Transport_Recommander/', 
                    credentialsId: 'githubPath'
            }
        }

        stage('Fetch Script from Main') {
            steps {
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

    post {
        success {
            echo '✅ Pipeline terminé avec succès.'
        }
        failure {
            echo '❌ Pipeline échoué.'
        }
    }
}
