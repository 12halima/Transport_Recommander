pipeline {
    agent any

    stages {
        stage('Checkout Jenkins Branch') {
            steps {
                // On reste sur jenkins-pipeline
                git branch: 'jenkins-pipeline', 
                    url: 'https://github.com/12halima/Transport_Recommander/', 
                    credentialsId: 'githubPath'
            }
        }

        stage('Fetch Script from Main') {
            steps {
                // On récupère uniquement le script depuis main
                sh '''
                    git fetch origin main
                    git checkout origin/main -- Process_GTFS-OSM/Network_Base.ipynb
                '''
            }
        }

        stage('Run PySpark Script') {
            steps {
                // Limite à 5 villes en mode Jenkins
                sh 'export JENKINS_MODE=1 && spark-submit Process_GTFS-OSM/Network_Base.ipynb'
            }
        }
    }
}
