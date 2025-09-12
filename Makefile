SHELL := /bin/bash
.ONESHELL:

-include .env
export

stackName ?= pq-responder-1
stackName := $(shell echo ${stackName} | tr '[:upper:]' '[:lower:]')
awsRegion ?= us-west-2
AWS_DEFAULT_REGION := ${awsRegion}
frontendConfigJson := ./frontend/src/config.json
packageJson := ./frontend/package.json
AgentFoundationalModel := us.anthropic.claude-sonnet-4-20250514-v1:0
UpdateQuestions ?= false
DeployFrontend ?= true
DeployIdp ?= true
ApiIntegrationTimeout ?= 29000

.PHONY : clean
clean :
	rm -rf .venv
	rm -rf .aws-sam
	rm -rf frontend/build
	rm -rf frontend/node_modules
	rm -rf .pytest_cache
	find . | grep -E "(/__pycache__$$|\.pyc$$|\.pyo$$)" | xargs rm -rf

.PHONY : init
init :
	python3.13 -m venv .venv
	source .venv/bin/activate
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt

	cp ${packageJson}.template ${packageJson}
	cd frontend
	npm install

.PHONY : deploy-backend
deploy-backend : 
	sam validate
	if [ $$? != 0 ]; \
	then \
		exit; \
	fi
	
	sam build
	if [ $$? != 0 ]; \
	then \
		exit; \
	fi

	sam deploy \
		--stack-name=${stackName} \
		--no-fail-on-empty-changeset \
		--no-disable-rollback \
		--parameter-overrides \
				EnableAPIGLogging=true  \
				AgentFoundationalModel=${AgentFoundationalModel} \
				UpdateQuestions=${UpdateQuestions} \
				DeployFrontend=${DeployFrontend} \
				DeployIdp=${DeployIdp} \
				ApiIntegrationTimeout=${ApiIntegrationTimeout}

.PHONY : sync-backend
sync-backend : 
	sam sync \
		--stack-name=${stackName} \
		--parameter-overrides \
				EnableAPIGLogging=true \
				AgentFoundationalModel=${AgentFoundationalModel}
				UpdateQuestions=${UpdateQuestions} \
				DeployFrontend=${DeployFrontend} \
				DeployIdp=${DeployIdp} \
				ApiIntegrationTimeout=${ApiIntegrationTimeout}


.PHONY : delete-backend
delete-backend: 
	sam delete \
		--stack-name=${stackName} \
		--no-prompts

	# Tidy up log groups that may have been left from custom resources
	echo Sleeping to make sure all logs have been written
	sleep 10

	# Delete all log groups for this stack
	echo "Deleting all log groups with prefix /aws/lambda/${stackName}"
	aws logs describe-log-groups --region ${awsRegion} --log-group-name-prefix "/aws/lambda/${stackName}-" | \
	jq -r '.logGroups[].logGroupName' | \
	while read -r logGroupName; do
		echo "Deleting Log Group $${logGroupName}"
		aws logs delete-log-group --log-group-name "$${logGroupName}"
	done

.PHONY : create-frontend-config
create-frontend-config :
	base_uri="http://localhost:3000"
	stackOutputs=$$(aws cloudformation describe-stacks --stack-name $${stackName} --query 'Stacks[0].Outputs')
	cognitoAuthority=$$(jq -r '.[] | select(.OutputKey == "CognitoProviderURL").OutputValue' <<< $${stackOutputs})
	cognitoDomain=$$(jq -r '.[] | select(.OutputKey == "CognitoUserPoolDomain").OutputValue' <<< $${stackOutputs})
	clientId=$$(jq -r '.[] | select(.OutputKey == "CognitoUserPoolClientId").OutputValue' <<< $${stackOutputs})

	jq -n \
		--arg redirect_uri "$${base_uri}" \
		--arg cognitoAuthority "$${cognitoAuthority}" \
		--arg logout_uri "$${base_uri}" \
		--arg cognitoDomain "$${cognitoDomain}" \
		--arg clientId "$${clientId}" \
		'
			{
				"authConfig": {
					"redirect_uri": $$redirect_uri,
					"authority": $$cognitoAuthority
				},
				"signOutConfig": {
					"logout_uri": $$logout_uri,
					"cognitoDomain": $$cognitoDomain
				},
				"client_id": $$clientId
			}' > ${frontendConfigJson}

.PHONY : update-frontend-deploy-config
update-frontend-deploy-config :
	tempFile=$$(mktemp)
	base_uri=$$(aws cloudformation describe-stacks --stack-name ${stackName} --query 'Stacks[0].Outputs[?OutputKey==`SiteCloudFrontUrl`].OutputValue' --output text)
	jq \
		--arg redirect_uri $${base_uri} \
		--arg logout_uri $${base_uri} \
		'.authConfig.redirect_uri = $$redirect_uri 
		| .signOutConfig.logout_uri = $$logout_uri' \
		${frontendConfigJson} > $${tempFile}
	cp $${tempFile} ${frontendConfigJson}

.PHONY : update-package-json
update-package-json :
	cloudfrontURL=$$(aws cloudformation describe-stacks --stack-name ${stackName} --query 'Stacks[0].Outputs[?OutputKey==`SiteCloudFrontUrl`].OutputValue' --output text)
	jq \
		--arg proxyUrl $${cloudfrontURL} \
		'.proxy = $$proxyUrl' \
		${packageJson}.template > ${packageJson}
		
.PHONY : run-frontend
run-frontend: create-frontend-config update-package-json
	cd frontend
	npm start

.PHONY : deploy-frontend
deploy-frontend : create-frontend-config update-frontend-deploy-config update-package-json
	cd frontend
	npm run build

	siteBucketName=$$( \
		aws cloudformation describe-stacks \
			--stack-name ${stackName} \
			--query 'Stacks[0].Outputs[?OutputKey==`SiteBucketName`].OutputValue' \
			--output text \
	)
	aws s3 sync build s3://$${siteBucketName} --exclude ".DS_Store"

	cloudFrontDistributionId=$$( \
		aws cloudformation describe-stacks \
			--stack-name ${stackName} \
			--query 'Stacks[0].Outputs[?OutputKey==`SiteCloudFrontDistributionId`].OutputValue' \
			--output text \
	)
	cloudFrontInvalidationId=$$( \
		aws cloudfront create-invalidation \
			--distribution-id $${cloudFrontDistributionId} \
			--paths "/*" \
			--query 'Invalidation.Id' \
			--output text \
	)
	cloudFrontInvalidationStatus=$$( \
		aws cloudfront get-invalidation \
			--distribution-id $${cloudFrontDistributionId} \
			--id $${cloudFrontInvalidationId} \
			--query 'Invalidation.Status' \
			--output text \
	)
	while [[ $${cloudFrontInvalidationStatus} == "InProgress" ]]
	do
		sleep 5
		cloudFrontInvalidationStatus=$$( \
			aws cloudfront get-invalidation \
				--distribution-id $${cloudFrontDistributionId} \
				--id $${cloudFrontInvalidationId} \
				--query 'Invalidation.Status' \
				--output text \
		)	
		echo Cloudfront Invalidation Status: $${cloudFrontInvalidationStatus}
	done
	
	
.PHONY : create_pytest_env
create_pytest_env :
	printf "def stack_name():\n  return '${stackName}'" > tests/environment/environment.py
	printf "\n\n" >> tests/environment/environment.py
	printf "def region():\n  return '${awsRegion}'" >> tests/environment/environment.py
	printf "\n\n" >> tests/environment/environment.py

.PHONY : unit
unit : create_pytest_env
	pytest tests/unit/ --cov --awsRegion=${awsRegion}

.PHONY : integration
integration : create_pytest_env
	pytest tests/integration/ --awsRegion=${awsRegion} --stackName=${stackName}

get-questions-% :
	getQuestionsFunction=$$(aws cloudformation describe-stacks \
		--stack-name ${stackName} \
		--query 'Stacks[0].Outputs[?OutputKey==`APIGetQuestionsFunction`].OutputValue' \
		--output text
	)

	startDate=$$(date -v-$*d "+%Y-%m-%d")
	endDate=$$(date "+%Y-%m-%d")
	payload=$$(
		jq \
			-n \
			--arg startDate $$startDate \
			--arg endDate $$endDate \
			' 
				{
					"startDate": $$startDate,
					"endDate": $$endDate
				}
			'
	)

	tempFile=$$(mktemp).json
	aws lambda invoke \
		--function-name $${getQuestionsFunction} \
		--payload "$${payload}" \
		--cli-binary-format raw-in-base64-out \
		--invocation-type RequestResponse \
		--cli-read-timeout 0 \
		$${tempFile}

	cat $${tempFile}

	rm $${tempFile}

get-publications :
	getCommitteePublicationsFunction=$$(aws cloudformation describe-stacks \
		--stack-name ${stackName} \
		--query 'Stacks[0].Outputs[?OutputKey==`APIGetCommitteePublicationsFunction`].OutputValue' \
		--output text
	)

	committeeId=203
	startDate=2022-01-01
	endDate=$$(date "+%Y-%m-%d")
	payload=$$(
		jq \
			-n \
			--arg committeeId $$committeeId \
			--arg startDate $$startDate \
			--arg endDate $$endDate \
			' 
				{
					"committeeId": $$committeeId,
					"startDate": $$startDate,
					"endDate": $$endDate
				}
			'
	)
	echo $${payload}
	tempFile=$$(mktemp).json
	aws lambda invoke \
		--function-name $${getCommitteePublicationsFunction} \
		--payload "$${payload}" \
		--cli-binary-format raw-in-base64-out \
		--invocation-type RequestResponse \
		--cli-read-timeout 0 \
		$${tempFile}

	cat $${tempFile}

	rm $${tempFile}

.PHONY : deploy
deploy : deploy-4

.PHONY : deploy-%
deploy-% : deploy-backend deploy-frontend get-questions-% get-publications
	
	siteCloudFrontUrl=$$(aws cloudformation describe-stacks \
		--stack-name ${stackName} \
		--query 'Stacks[0].Outputs[?OutputKey==`SiteCloudFrontUrl`].OutputValue' \
		--output text
	)
	@echo SiteCloudFrontUrl = $${siteCloudFrontUrl}

.PHONY : delete
delete : delete-backend
