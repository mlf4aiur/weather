node {
    // Mark the code checkout 'stage'....
    stage 'Checkout'

    // Get source code from GitHub
    git credentialsId: cred_git, url: 'https://github.com/mlf4aiur/weather.git'

    // Mark the code test 'stage'....
    stage 'Test'
    // Run the unit test
    runTests('test_weather.py')

    // Mark the code build 'stage'....
    stage 'Bake Docker image'
    // Run the docker build
    def v = version('weather.py')
    def docker_tag = "${v}-${env.BUILD_NUMBER}"
    def dockerRepoName = 'kevin/weather'
    def image = docker.build(dockerRepoName, '.')

    // Push Docker image to private Docker registry
    stage 'Private Docker Registry'
    // Docker registry server defined in Jenkins global properties
    docker.withRegistry("${env.DKR_SERVER}", cred_dkr) {
        image.push()
        image.push("${docker_tag}")
    }

    stage 'Staging'
    input message: 'Deploy it to Staging?', submitter: 'admin'

    // Deploy this service to Staging environment
    withCredentials([[$class: 'UsernamePasswordMultiBinding',
                      credentialsId: cred_aws,
                      usernameVariable: 'AWS_ACCESS_KEY_ID',
                      passwordVariable: 'AWS_SECRET_ACCESS_KEY']]) {
        withEnv(["AWS_DEFAULT_REGION=${region}",
                 "CLUSTER_NAME=${cluster_name}",
                 "SERVICE_NAME=${service_name}",
                 "REPO_NAME=${dockerRepoName}",
                 "TAG=${docker_tag}"]) {
            sh '''
                set +x
                echo AWS_DEFAULT_REGION: ${AWS_DEFAULT_REGION}
                echo CLUSTER_NAME: ${CLUSTER_NAME}
                echo SERVICE_NAME: ${SERVICE_NAME}

                docker run \\
                --rm \\
                -e "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" \\
                -e "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" \\
                -e "AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}" \\
                silintl/ecs-deploy \\
                -c ${CLUSTER_NAME} \\
                -n ${SERVICE_NAME} \\
                -i ${env.DKR_SERVER}/${REPO_NAME}:${TAG} \\
                -m 50 \\
                -M 100 \\
                -t 240
            '''
        }
    }
}

stage name: 'Staging', concurrency: 1
node {
    deploy 'staging'
}

input message: "Does staging look good?"
try {
    checkpoint('Before production')
} catch (NoSuchMethodError _) {
    echo 'Checkpoint feature available in CloudBees Jenkins Enterprise.'
}

stage name: 'Production', concurrency: 1
node {
    echo 'Production server looks to be alive'
    deploy 'production'
    echo "Deployed to production"
}

def version(versionFile) {
    def matcher = readFile(versionFile) =~ '__version__ = \'(.+)\''
    matcher ? matcher[0][1] : '0.0.1'
}

def runTests(testFile) {
    sh "docker run --rm -v ${env.JENKINS_HOME}/workspace/${env.JOB_NAME}/:/myapp -w /myapp python:3.5.2-alpine pip install -r requirements.txt && python test_weather.py"
}

def deploy(id) {
    sh "echo ${id}"
}
