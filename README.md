# testFlask-tekton

Sample Tekton Pipeline for a Flask Python Application

Application will show how we can use Tekton to deploy/test a flask application running on openshift, the Application being used is [testFlask](https://github.com/MoOyeg/testFlask.git)  
Environment variables used in Commands have samples in the sample_env file.  
So this example assumes a pipeline scenario where there is a running production application represented by our Production Project and at build time we deploy the same exact infrastructure in our devlopment project and test the code, when all satisfied we promote our dev image to production which is automatically deployed based on a trigger from our imagestream.

## Pre-Requisites:

Install Openshift Pipelines Operator  
https://docs.openshift.com/container-platform/4.6/pipelines/installing-pipelines.html

## Steps to Run via Kustomize

### 1 Create Dev Environment

`oc apply -k ./overlays/dev`

### 2 Create Prod Environment

`oc apply -k ./overlays/prod`

### 3 Create CICD Environment

Respository provides examples on how to deploy a normal tekton CICD Pipeline and a version that provides Image Scanning and Policy Checking using Red hat's Advanced Cluster Security Product.

**_Deploy pipeline without scanning and security_**  
`kustomize build ./cicd/overlays/simple | sed -e 's/name: testflask-pipelinerun/# name: testflask-pipelinerun/' | oc create -f -`

**_Create CICD Environment with ACS_**  
Please see Notes below before running this command  
`kustomize build ./cicd/overlays/secure | sed -e 's/name: testflask-pipelinerun/# name: testflask-pipelinerun/' | oc create -f -`

### Notes

1 If using the internal openshift registry ACS requires integration to the internal openshift registry and access to pull.You can try using the below command to create this(This might not be updated).  
 `kustomize build ./cicd/overlays/secure/acs/pipelines-and-secrets | oc create -f -`

2 ACS roxctl requires a secret that contains the Central cluster url and the API Token.You can try using the below command to create this(This might not be updated).  
`kustomize build ./cicd/overlays/secure/acs/pipelines-and-secrets | oc create -f -`

To use the eventlistener remember to create a webhook

PipelineRun will start in pending, re-run to start Build

---

<!---
### Steps to Run via oc/kubectl commands  

1 **Source Sample Environment**  
```eval "$(curl https://raw.githubusercontent.com/MoOyeg/testFlask/master/sample_env)"```  

2 **Create a new project for Tekton Pipeline**  
```oc new-project $TEKTON_NAMESPACE```  

3 **Create prod and test projects for your pipeline**  

- Create Projects  
  ```oc new-project $NAMESPACE_DEV```  
  ```oc new-project $NAMESPACE_PROD```  
  
  - Give Permissions to Tekton Pipeline User on Test and Prod Namespaces so we can build in those namespaces  
  ```oc adm policy add-cluster-role-to-user admin system:serviceaccount:$TEKTON_NAMESPACE:pipeline -n $NAMESPACE_DEV```  
  ```oc adm policy add-cluster-role-to-user admin system:serviceaccount:$TEKTON_NAMESPACE:pipeline -n $NAMESPACE_PROD```  
  ```oc adm policy add-cluster-role-to-user admin system:serviceaccount:$TEKTON_NAMESPACE:pipeline -n $TEKTON_NAMESPACE```  

  - Create our Infrastructure Secret in our Development and Production  
  ```oc create secret generic ${SECRET_NAME} --from-literal=MYSQL_USER=$MYSQL_USER --from-literal=MYSQL_PASSWORD=$MYSQL_PASSWORD -n $NAMESPACE_DEV```  
  ```oc create secret generic ${SECRET_NAME} --from-literal=MYSQL_USER=$MYSQL_USER --from-literal=MYSQL_PASSWORD=$MYSQL_PASSWORD -n $NAMESPACE_PROD```  
  
  - Create our Database in Production  
  ```oc new-app $MYSQL_HOST --env=MYSQL_DATABASE=$MYSQL_DATABASE -l db=${MYSQL_HOST} -l app=${APP_NAME} --as-deployment-config=true -n ${NAMESPACE_PROD}```  
  
  - Set our Secret on the Production Database  
  ```oc set env dc/$MYSQL_HOST --from=secret/${SECRET_NAME} -n $NAMESPACE_PROD```  

  - Create our Production Application  
  ```oc new-app ${CODE_URL} --name=$APP_NAME -l app=${APP_NAME} --strategy=source --env=APP_CONFIG=${APP_CONFIG} --env=APP_MODULE=${APP_MODULE} --env=MYSQL_HOST=$MYSQL_HOST --env=MYSQL_DATABASE=$MYSQL_DATABASE --as-deployment-config=true -n $NAMESPACE_PROD```  
  
  - Set our Secret on the Production Application  
  ```oc set env dc/$APP_NAME --from=secret/${SECRET_NAME} -n $NAMESPACE_PROD```  

  - Expose our Production Application to the External World  
  ```oc expose svc/$APP_NAME -n $NAMESPACE_PROD```
  
  - Label our Projects for the Development Console  

  ``` console
     oc label dc/$APP_NAME app.kubernetes.io/part-of=$APP_NAME -n $NAMESPACE_PROD
     oc label dc/$MYSQL_HOST app.kubernetes.io/part-of=$APP_NAME -n $NAMESPACE_PROD
     oc annotate dc/$APP_NAME app.openshift.io/connects-to=$MYSQL_HOST -n $NAMESPACE_PROD
  ```

4 **Create Pipeline Components**  

- Create PVC for Tekton Workspace  
    ```curl https://raw.githubusercontent.com/MoOyeg/testFlask-tekton/master/cli-create/pipeline-pvc.yaml | envsubst | oc create -f -```  

  - Create custom task  
    ```curl https://raw.githubusercontent.com/MoOyeg/testFlask-tekton/master/cli-create/task-python-unittest.yaml | envsubst '$TEKTON_NAMESPACE' | oc create -f -```  

  - Create Resources  
    ```curl https://raw.githubusercontent.com/MoOyeg/testFlask-tekton/master/cli-create/pipelineresource-git.yaml | envsubst | oc create -f -```  

  - Create Pipeline  
    ```curl https://raw.githubusercontent.com/MoOyeg/testFlask-tekton/master/cli-create/pipeline-testflask.yaml | envsubst | oc create -f -```  

5 **Start Pipeline Execution by Creating PipelineRun**  

- Create PipelineRun  
   ```curl https://raw.githubusercontent.com/MoOyeg/testFlask-tekton/master/cli-create/pipelinerun-testflask.yaml | envsubst | oc create -f -```
