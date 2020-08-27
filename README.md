# testFlask-tekton
## Tekton Pipeline for the testFlask Repo

This Repo Provides a sample Tekton Pipeline for the [testFlask Repo
](https://github.com/MoOyeg/testFlask)


oc new-project $TEKTON_NAMESPACE

oc adm policy add-cluster-role-to-user admin system:serviceaccount:$TEKTON_NAMESPACE:pipeline -n $NAMESPACE_DEV
oc adm policy add-cluster-role-to-user admin system:serviceaccount:$TEKTON_NAMESPACE:pipeline -n $NAMESPACE_PROD 
oc adm policy add-cluster-role-to-user admin system:serviceaccount:$TEKTON_NAMESPACE:pipeline -n $TEKTON_NAMESPACE