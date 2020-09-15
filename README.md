# testFlask-tekton
Sample Tekton Pipeline for a Flask Python Application<br/>
Application will show how we can use Tekton to deploy/test a flask application running on openshift, the Application being used is [testFlask](https://github.com/MoOyeg/testFlask.git)<br/>
Environment variables used in Commands have samples in the sample_env file.<br/>
So this example assumes a pipeline scenario where there is a running production application represented by our Production Project($NAMESPACE_PROD) and at build time we deploy the same exact infrastructure in our devlopment project ($NAMESPACE_DEV) and test, when all satisfied we promote our dev image to production which is automatically deployed based on a trigger from our imagestream.

### Steps to Run<br/>
1 **Source Sample Environment**<br/>
```source ./sample_env```<br/>

2 **Create a new project for Tekton Pipeline**<br/>
```oc new-project $TEKTON_NAMESPACE```<br/>

3 **Create prod and test projects for your pipeline**<br/>
  - Create Projects <br/>
  ```oc new-project $NAMESPACE_DEV```<br/>
  ```oc new-project $NAMESPACE_PROD```<br/>
  
  - Give Permissions to Tekton Pipeline User on Test and Prod Namespaces so we can build in those namespaces<br/>
  ```oc adm policy add-cluster-role-to-user admin system:serviceaccount:$TEKTON_NAMESPACE:pipeline -n $NAMESPACE_DEV```<br/>
  ```oc adm policy add-cluster-role-to-user admin system:serviceaccount:$TEKTON_NAMESPACE:pipeline -n $NAMESPACE_PROD```<br/>
  ```oc adm policy add-cluster-role-to-user admin system:serviceaccount:$TEKTON_NAMESPACE:pipeline -n $TEKTON_NAMESPACE```<br/>

  - Create our Infrastructure Secret in our Development and Production<br/>
  ```oc create secret generic ${SECRET_NAME} --from-literal=MYSQL_USER=$MYSQL_USER --from-literal=MYSQL_PASSWORD=$MYSQL_PASSWORD -n $NAMESPACE_DEV```<br/>
  ```oc create secret generic ${SECRET_NAME} --from-literal=MYSQL_USER=$MYSQL_USER --from-literal=MYSQL_PASSWORD=$MYSQL_PASSWORD -n $NAMESPACE_PROD```<br/>
  
  - Create our Database in Production<br/>
  ```oc new-app $MYSQL_HOST --env=MYSQL_DATABASE=$MYSQL_DB -l db=${MYSQL_HOST} -l app=${APP_NAME} --as-deployment-config=true -n ${NAMESPACE_PROD}```<br/>
  
  - Set our Secret on the Production Database<br/>
  ```oc set env dc/$MYSQL_HOST --from=secret/${SECRET_NAME} -n $NAMESPACE_PROD```<br/>
   
  - Create our Production Application<br/>
  ```oc new-app ${CODE_URL} --name=$APP_NAME -l app=${APP_NAME} --strategy=source --env=APP_CONFIG=${APP_CONFIG} --env=APP_MODULE=${APP_MODULE} --env=MYSQL_HOST=$MYSQL_HOST --env=MYSQL_DB=$MYSQL_DB --as-deployment-config=true -n $NAMESPACE_PROD```<br/>
  
  - Set our Secret on the Production Application<br/>
  ```oc set env dc/$APP_NAME --from=secret/${SECRET_NAME} -n $NAMESPACE_PROD```
 
  - Expose our Production Application to the External World<br/>
  ```oc expose svc/$APP_NAME -n $NAMESPACE_PROD```
  
  - Label our Projects for the Development Console<br/>
  ```
     oc label dc/$APP_NAME app.kubernetes.io/part-of=$APP_NAME -n $NAMESPACE_PROD
     oc label dc/$MYSQL_HOST app.kubernetes.io/part-of=$APP_NAME -n $NAMESPACE_PROD
     oc annotate dc/$APP_NAME app.openshift.io/connects-to=$MYSQL_HOST -n $NAMESPACE_PROD
  ```

4 **Create Pipeline Components**<br/>
  - Create PVC for Tekton Workspace<br/>
    ```curl https://raw.githubusercontent.com/MoOyeg/testFlask-tekton/master/pipeline-pvc.yaml | envsubst | oc create -f -```<br/>

  - Create custom task<br/>
    ```curl https://raw.githubusercontent.com/MoOyeg/testFlask-tekton/master/task-python-unittest.yaml | envsubst '$TEKTON_NAMESPACE' | oc create -f -```<br/>

  - Create Resources<br/>
    ```curl https://raw.githubusercontent.com/MoOyeg/testFlask-tekton/master/pipelineresource-git.yaml | envsubst | oc create -f -```<br/>

  - Create Pipeline<br/>
    ```curl https://raw.githubusercontent.com/MoOyeg/testFlask-tekton/master/pipeline-testflask.yaml | envsubst | oc create -f -```<br/>

5 **Start Pipeline Execution by Creating PipelineRun**<br/>
  - Create PipelineRun<br/>
   ```curl https://raw.githubusercontent.com/MoOyeg/testFlask-tekton/master/pipelinerun-testflask.yaml | envsubst | oc create -f -```<br/>