# @title Tekton Pipeline Git Resolvers must use Organization Approved Git Repositories
#
# All Pipeline Git Resolvers must use Organization Approved Git Repositories
# 
# 
#
#

package main

default is_gatekeeper = false
org_allowed_bundle_registries := ["quay.io","registry.redhat.io"]

#Check if we are using gatekeeper
is_gatekeeper {
	has_field(input, "review")
	has_field(input.review, "object")
}

#Input is Gatekeeper
resource = input.review.object {
	is_gatekeeper
}

# Input is not from gatekeeper
resource = input {
	not is_gatekeeper
}

# Set the .metadata.name of the object we are currently working on
resource_name = resource.metadata.name

# Set the kind of the object
resource_kind = resource.kind

#set taskref_filter
taskref_filter := resource.spec.tasks[0].taskRef.params

only_correct_bundle_value_negate(k) {
	not only_correct_bundle_value(k)
}

only_correct_bundle_value(k) {
    some i
    contains(resource.spec.tasks[0].taskRef.params[k].value ,org_allowed_bundle_registries[i])   
}

any_bundle_taskref  {    
	some i
    resource.spec.tasks[i].taskRef.resolver == "bundles"
    upper(resource.spec.tasks[i].taskRef.kind) == "TASK"
    some j
    resource.spec.tasks[0].taskRef.params[j].name == "bundle"
    only_correct_bundle_value_negate(j)
}

violation[{"msg": msg}] {
	resource_kind == "Pipeline"
    any_bundle_taskref 
    
    msg := sprintf("Denied -- Pipeline %v is using a Bundle Resolver not in Organization Approved List. Approved Bundle Registries %v", [resource_name,org_allowed_bundle_registries])
}

has_field(obj, field) {
	not object.get(obj, field, "N_DEFINED") == "N_DEFINED"
}

missing_field(obj, field) {
	obj[field] == ""
}

missing_field(obj, field) {
	not has_field(obj, field)
}