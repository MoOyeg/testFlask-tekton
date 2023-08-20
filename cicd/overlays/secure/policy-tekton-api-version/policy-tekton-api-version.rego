# @title Tekton PipelineRuns must have a Failure Timeout Set
#
# All PipelineRuns must have a Failure Timeout
# 
# 
#
#

package main

default is_gatekeeper = false
org_approved_api_version := ["tekton.dev/v1","tekton.dev/v1beta1"]

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

# Set the apiVersion of the object
resource_api_version = resource.apiVersion


any_approved_apiversion_negate {
	not any_approved_apiversion
}

any_approved_apiversion {
	some i
	org_approved_api_version[i] == resource_api_version
}

violation[{"msg": msg}] {
	resource_kind == "Pipeline"
    any_approved_apiversion_negate
    
    msg := sprintf("Denied -- Pipeline %v not using an Approved API Version. Approved API Versions are %v", [resource_name,org_approved_api_version])
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