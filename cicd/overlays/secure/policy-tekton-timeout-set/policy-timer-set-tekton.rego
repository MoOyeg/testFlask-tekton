# @title Tekton PipelineRuns must have a Failure Timeout Set
#
# All PipelineRuns must have a Failure Timeout
# 
# 
#
#

package main

default is_gatekeeper = false
org_policy_max_timeout = "3h"

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

violation[{"msg": msg}] {
	resource_kind == "PipelineRun"
	#missing_field(resource.spec,"timeouts")
    missing_field(resource.spec.timeouts,"pipeline")
    msg := sprintf("Denied -- PipelineRun %v does not have a max failure timeout set. This is required by Org Policy", [resource_name])
}

violation[{"msg": msg}] {
    resource_kind == "PipelineRun"
    resource_timeout := (time.parse_duration_ns(resource.spec.timeouts["pipeline"]))/100000000
    policy_duration2 := (time.parse_duration_ns(org_policy_max_timeout))/100000000
    resource_timeout >= policy_duration2
    msg := sprintf("Denied -- PipelineRun %v max failure timeout set to High.Timeout cannot be higher than %v.", [resource_name,org_policy_max_timeout])
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
