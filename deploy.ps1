<#!
.SYNOPSIS
Builds and securely deploys the expense processor to Cloud Run.

.DESCRIPTION
The Cloud Run service remains IAM-protected. The final command also removes a
pre-existing allUsers Invoker grant that may have been created by an earlier
--allow-unauthenticated deployment.
#>

$ErrorActionPreference = 'Stop'

$projectId = 'test-project-463904'
$region = 'asia-south1'
$serviceName = 'expense-processor'
$image = "$region-docker.pkg.dev/$projectId/cloud-run-source-deploy/$serviceName"
$gcloud = 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd'

& $gcloud builds submit . --tag $image --project $projectId

& $gcloud run deploy $serviceName `
    --image $image `
    --project $projectId `
    --region $region `
    --platform managed `
    --no-allow-unauthenticated `
    --update-secrets '/secrets/service_account.json=my-service-account-json:latest'

# Revoke public invocation only if an earlier deployment granted it.
$publicInvoker = & $gcloud run services get-iam-policy $serviceName `
    --project $projectId `
    --region $region `
    --flatten 'bindings[].members' `
    --filter 'bindings.role=roles/run.invoker AND bindings.members=allUsers' `
    --format 'value(bindings.members)'

if ($publicInvoker -eq 'allUsers') {
    & $gcloud run services remove-iam-policy-binding $serviceName `
        --project $projectId `
        --region $region `
        --member 'allUsers' `
        --role 'roles/run.invoker'
}
