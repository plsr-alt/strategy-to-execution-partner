#!/bin/bash

# ============================================
# YouTube Automation EC2 Auto Start/Stop Deploy Script
# ============================================

set -e

# Configuration
STACK_NAME="youtube-automation-ec2-schedule"
TEMPLATE_FILE="ec2_automation_stack.yaml"
REGION="ap-northeast-1"
INSTANCE_ID="i-02ae03f0b54d46ac1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}YouTube Automation EC2 Schedule Deploy${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# ============================================
# Step 1: Check Prerequisites
# ============================================
echo -e "${YELLOW}[Step 1] Checking prerequisites...${NC}"

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed${NC}"
    exit 1
fi

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}❌ Template file not found: $TEMPLATE_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites OK${NC}"
echo ""

# ============================================
# Step 2: Verify AWS Credentials
# ============================================
echo -e "${YELLOW}[Step 2] Verifying AWS credentials...${NC}"

if ! aws sts get-caller-identity --region "$REGION" > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS authentication failed${NC}"
    echo "Please configure AWS CLI credentials:"
    echo "  aws configure"
    exit 1
fi

AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✅ Authenticated to AWS Account: $AWS_ACCOUNT${NC}"
echo ""

# ============================================
# Step 3: Validate CloudFormation Template
# ============================================
echo -e "${YELLOW}[Step 3] Validating CloudFormation template...${NC}"

if ! aws cloudformation validate-template \
    --template-body "file://$TEMPLATE_FILE" \
    --region "$REGION" > /dev/null 2>&1; then
    echo -e "${RED}❌ Template validation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Template validation passed${NC}"
echo ""

# ============================================
# Step 4: Check if Stack Already Exists
# ============================================
echo -e "${YELLOW}[Step 4] Checking if stack already exists...${NC}"

STACK_EXISTS=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].StackName' \
    --output text 2>/dev/null || echo "NONE")

if [ "$STACK_EXISTS" != "NONE" ]; then
    echo -e "${YELLOW}⚠️  Stack already exists: $STACK_NAME${NC}"
    echo "Updating stack instead of creating new one..."
    echo ""

    echo -e "${YELLOW}[Step 5] Updating CloudFormation stack...${NC}"

    aws cloudformation update-stack \
        --stack-name "$STACK_NAME" \
        --template-body "file://$TEMPLATE_FILE" \
        --parameters "ParameterKey=InstanceId,ParameterValue=$INSTANCE_ID" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$REGION"

    echo -e "${GREEN}✅ Stack update initiated${NC}"

    echo -e "${YELLOW}Waiting for stack update to complete...${NC}"
    aws cloudformation wait stack-update-complete \
        --stack-name "$STACK_NAME" \
        --region "$REGION" || echo -e "${YELLOW}⚠️  Stack update may have no changes${NC}"

else
    echo -e "${YELLOW}[Step 5] Creating CloudFormation stack...${NC}"

    aws cloudformation create-stack \
        --stack-name "$STACK_NAME" \
        --template-body "file://$TEMPLATE_FILE" \
        --parameters "ParameterKey=InstanceId,ParameterValue=$INSTANCE_ID" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$REGION"

    echo -e "${GREEN}✅ Stack creation initiated${NC}"

    echo -e "${YELLOW}Waiting for stack creation to complete...${NC}"
    aws cloudformation wait stack-create-complete \
        --stack-name "$STACK_NAME" \
        --region "$REGION"

fi

echo -e "${GREEN}✅ Stack deployment completed${NC}"
echo ""

# ============================================
# Step 6: Get Stack Outputs
# ============================================
echo -e "${YELLOW}[Step 6] Stack outputs:${NC}"

aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[].[OutputKey,OutputValue]' \
    --output table

echo ""

# ============================================
# Step 7: List EventBridge Rules
# ============================================
echo -e "${YELLOW}[Step 7] EventBridge rules:${NC}"

aws events list-rules \
    --name-prefix "youtube-automation" \
    --region "$REGION" \
    --query 'Rules[].[Name,State,ScheduleExpression]' \
    --output table

echo ""

# ============================================
# Step 8: Optional - Test Lambda
# ============================================
echo -e "${YELLOW}[Step 8] Lambda function test (optional)${NC}"
echo "Run the following commands to test:"
echo ""
echo "# Test START:"
echo "aws lambda invoke \\"
echo "  --function-name youtube-automation-ec2-control \\"
echo "  --payload '{\"action\":\"start\"}' \\"
echo "  --region $REGION \\"
echo "  response.json && cat response.json"
echo ""
echo "# Test STOP:"
echo "aws lambda invoke \\"
echo "  --function-name youtube-automation-ec2-control \\"
echo "  --payload '{\"action\":\"stop\"}' \\"
echo "  --region $REGION \\"
echo "  response.json && cat response.json"
echo ""

# ============================================
# Step 9: Summary
# ============================================
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Test Lambda with commands above"
echo "  2. Verify EC2 instance state changes"
echo "  3. Check CloudWatch Logs:"
echo "     aws logs tail /aws/lambda/youtube-automation-ec2-control --follow"
echo ""
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Instance ID: $INSTANCE_ID"
echo ""
echo "To delete stack:"
echo "  aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION"
echo ""
