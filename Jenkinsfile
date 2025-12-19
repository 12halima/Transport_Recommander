pipeline {
    agent any

    stages {
        stage('Checkout Jenkins Branch') {
            steps {
                git branch: 'jenkins-pipeline', 
                    url: 'https://github.com/12halima/Transport_Recommander/', 
                    credentialsId: 'githubPath'
            }
        }

        stage('Get Script from Main') {
            steps {
                sh 'git fetch origin main && git checkout origin/main -- Process_GTFS-OSM/Network_Base.ipynb'
            }
        }

        stage('Run PySpark Script') {
            steps {
                sh 'export JENKINS_MODE=1 && spark-submit Process_GTFS-OSM/Network_Base.ipynb'
            }
        }
    }
}
