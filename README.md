# testFlask-tekton

Sample Tekton Pipeline for a Flask Python Application

Application will show how we can use Tekton to deploy/test a flask application running on openshift, the Application being used is [testFlask](https://github.com/MoOyeg/testFlask.git)  
Environment variables used in Commands have samples in the sample_env file.  
So this example assumes a pipeline scenario where there is a running production application represented by our Production Project and at build time we deploy the same exact infrastructure in our devlopment project and test the code, when all satisfied we promote our dev image to production which is automatically deployed based on a trigger from our imagestream.

## Prerequisites:
- OpenShift Cluster >=4.10

- [Install Openshift Pipelines Operator](https://docs.openshift.com/container-platform/4.11/cicd/pipelines/op-release-notes.html)

- If using the Secure Pipeline Example then [Red Hat Advanced Cluster Security Operator](https://docs.openshift.com/acs/3.74/installing/installing_ocp/install-rhacs-ocp.html) is Required.

- If the Gatekeeper Example is required then install the Gatekeeper Operator from Operatorhub

## Steps to Run via Kustomize

- [Create Prerequisite Infrastucture Components if Required](#prerequisite-infrastructure)

- Create Dev Environment

  ```bash
  oc apply -k ./overlays/dev
  ```

- Create Prod Environment

  ```bash
  oc apply -k ./overlays/prod
  ```

- Create CICD Environment
  Respository provides examples on how to deploy a normal tekton CICD Pipeline and a version that provides Image Scanning and Policy Checking using Red hat's Advanced Cluster Security Product.Depending on your version of OpenShift the default run of the pipeline might fail, please read Notes below.

  - **_Deploy pipeline without scanning and security_**  
    ```bash
    oc kustomize ./cicd/overlays/simple | sed -e 's/name: testflask-pipelinerun/# name: testflask-pipelinerun/' | oc create -f -
    ```

  - **_Create CICD Environment with ACS_**  
  Please see [Notes](#notes) if you run into errors

    ```bash
    oc kustomize ./cicd/overlays/secure | sed -e 's/name: testflask-pipelinerun/# name: testflask-pipelinerun/' | oc create -f -
    ```

## Prerequisite Infrastructure
Please note this section is not maintained and is pulled from other repos.

- Install Openshift Pipelines Operator
  ```bash
  oc apply -k ./infra/pipeline-operator
  ```

- Install Advanced Cluster Security Operator

  ```bash
  oc apply -k ./infra/acs-operator
  ```

- Create Advanced Cluster Security Instance

  ```bash
  oc apply -k ./infra/acs-instance
  ```

- Install Gatekeeper Operator

  ```bash
  oc apply -k ./infra/gatekeeper-operator
  ```
## Notes

- Error('image-scan-pod" is waiting to start: CreateContainerConfigError').With error ('Error: secret "roxsecrets" not found'). ACS roxctl requires a secret that contains the Central cluster url and the API Token. You can try using the below command to create this(This might not be updated).  
  ```bash
  oc kustomize ./cicd/overlays/secure/acs/pipelines-and-secrets | oc create -f -
  ```

- Error - unable to validate against any security context constraint for builah task when running Pipeline
Depending on your version of openshift pipelines the buildah task might require an enhanced scc.  

  ```bash
  oc project 1234-tekton && oc adm policy add-scc-to-user privileged -z pipeline
  ```
  ```bash
  oc adm policy add-scc-to-user privileged system:serviceaccount:1234-tekton:pipeline
  ```
  ```bash
  oc policy add-role-to-user system:image-pusher system:serviceaccount:1234-tekton:pipeline
  ```

- If you get "error creating build container: Error initializing source docker://registry.redhat.io/ubi8/ubi:latest: unable to retrieve auth token". This means the docker file we are using for build is not using the internal openshift registry.We might have to update the dockerfile to build.
  ```bash
  oc tag --source=docker registry.redhat.io/ubi8/ubi:latest ubi8:latest -n openshift
  ```

- To use the eventlistener remember to create a webhook  

- PipelineRun will start in pending, re-run to start Build  

<!-- 1 If using the internal openshift registry ACS requires integration to the internal openshift registry and access to pull.You can try using the below command to create this(This might not be updated).  
 `kustomize build ./cicd/overlays/secure/acs/pipelines-and-secrets | oc create -f -` -->

## Gatekeeper Enforcement 
With the use of the Gatekeeper/OPA you can create policies to enforce/inform of cluster violations.There are sample policies to show an example of enforcing with tekton.Please make sure to install the gatekeeper operator first.

Make sure all tekton pipelines have an ACS Policy Checking Task(Might need to run it 2x as API has to create CRD for contraint)  
```bash
oc kustomize ./cicd/overlays/secure/acs/policy-tekton-checking | oc create -f -
```

Make sure all tekton pipelines have an ACS Policy Scanning Task(Might need to run it 2x as API has to create CRD for contraint)  
```bash
oc kustomize ./cicd/overlays/secure/acs/policy-tekton-scanning | oc create -f -
```

After the above constraints are created, you should not longer be able to run the non-secure pipeline creation above but you should be able to run the secure version.

