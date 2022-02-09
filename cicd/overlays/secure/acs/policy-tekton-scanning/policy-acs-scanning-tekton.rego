# @title Tekton Pipelines must use ACS Tasks to Shift Left
#
# All Pipelines must scan images for vulnerabilities
# 
# 
#
# 

package main

default is_gatekeeper = false

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

no_any_stackrox_scan_task_negation {
	not any_stackrox_scan_task
}

any_stackrox_scan_task {
	some i
	resource.spec.tasks[i].taskRef.kind == "ClusterTask"
	name := resource.spec.tasks[i].taskRef.name
	name == "rox-image-scan"
}

violation[{"msg": msg}] {
	resource_kind == "Pipeline"

	no_any_stackrox_scan_task_negation

	msg := sprintf("Denied -- Pipeline %v does not have the ACS ClusterTask for image Scanning(rox-image-scan), This is required by Policy", [resource_name])
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
