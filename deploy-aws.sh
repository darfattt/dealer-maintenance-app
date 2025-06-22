#!/bin/bash

# =============================================================================
# DEALER DASHBOARD - AWS DEPLOYMENT SCRIPT
# =============================================================================
# This script deploys the Dealer Dashboard to AWS using Docker Compose
# Supports EC2, ECS, and other AWS deployment methods

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_TYPE=${1:-"ec2"}  # ec2, ecs, or fargate
AWS_REGION=${AWS_REGION:-"us-east-1"}
KEY_PAIR_NAME=${KEY_PAIR_NAME:-"dealer-dashboard-key"}
SECURITY_GROUP_NAME=${SECURITY_GROUP_NAME:-"dealer-dashboard-sg"}
INSTANCE_TYPE=${INSTANCE_TYPE:-"t3.large"}
DOMAIN_NAME=${DOMAIN_NAME:-""}

echo ""
echo -e "${BLUE}========================================"
echo -e "  🚀 AWS Deployment - Dealer Dashboard"
echo -e "  🌍 Region: ${AWS_REGION}"
echo -e "  📦 Type: ${DEPLOYMENT_TYPE}"
echo -e "========================================${NC}"
echo ""

# Function to check AWS CLI
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}❌ AWS CLI not found. Please install AWS CLI first.${NC}"
        echo -e "${YELLOW}💡 Install: https://aws.amazon.com/cli/${NC}"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        echo -e "${RED}❌ AWS credentials not configured.${NC}"
        echo -e "${YELLOW}💡 Run: aws configure${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ AWS CLI configured${NC}"
}

# Function to create security group
create_security_group() {
    echo -e "${YELLOW}🔒 Creating security group...${NC}"
    
    # Check if security group exists
    if aws ec2 describe-security-groups --group-names "$SECURITY_GROUP_NAME" --region "$AWS_REGION" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️ Security group already exists${NC}"
        return
    fi
    
    # Create security group
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name "$SECURITY_GROUP_NAME" \
        --description "Security group for Dealer Dashboard" \
        --region "$AWS_REGION" \
        --query 'GroupId' \
        --output text)
    
    # Add rules
    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region "$AWS_REGION"
    
    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region "$AWS_REGION"
    
    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 \
        --region "$AWS_REGION"
    
    # Application ports
    for port in 5000 8000 8080 8100 8200 8501 8502; do
        aws ec2 authorize-security-group-ingress \
            --group-id "$SECURITY_GROUP_ID" \
            --protocol tcp \
            --port "$port" \
            --cidr 0.0.0.0/0 \
            --region "$AWS_REGION"
    done
    
    echo -e "${GREEN}✅ Security group created: ${SECURITY_GROUP_ID}${NC}"
}

# Function to create key pair
create_key_pair() {
    echo -e "${YELLOW}🔑 Creating key pair...${NC}"
    
    if [ -f "${KEY_PAIR_NAME}.pem" ]; then
        echo -e "${YELLOW}⚠️ Key pair file already exists${NC}"
        return
    fi
    
    aws ec2 create-key-pair \
        --key-name "$KEY_PAIR_NAME" \
        --region "$AWS_REGION" \
        --query 'KeyMaterial' \
        --output text > "${KEY_PAIR_NAME}.pem"
    
    chmod 400 "${KEY_PAIR_NAME}.pem"
    
    echo -e "${GREEN}✅ Key pair created: ${KEY_PAIR_NAME}.pem${NC}"
}

# Function to deploy to EC2
deploy_ec2() {
    echo -e "${BLUE}🖥️ Deploying to EC2...${NC}"
    
    # Get latest Amazon Linux 2 AMI
    AMI_ID=$(aws ec2 describe-images \
        --owners amazon \
        --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
        --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
        --output text \
        --region "$AWS_REGION")
    
    echo -e "${YELLOW}📀 Using AMI: ${AMI_ID}${NC}"
    
    # Create user data script
    cat > user-data.sh << 'EOF'
#!/bin/bash
yum update -y
yum install -y docker git

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Start Docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Clone repository (you'll need to update this with your repo)
cd /home/ec2-user
git clone https://github.com/yourusername/dealer-dashboard.git
cd dealer-dashboard

# Copy environment file
cp .env.production .env

# Start services
docker-compose -f docker-compose.production.yml up -d

# Create startup script
cat > /home/ec2-user/start-dashboard.sh << 'SCRIPT'
#!/bin/bash
cd /home/ec2-user/dealer-dashboard
docker-compose -f docker-compose.production.yml up -d
SCRIPT

chmod +x /home/ec2-user/start-dashboard.sh
chown ec2-user:ec2-user /home/ec2-user/start-dashboard.sh
EOF
    
    # Launch instance
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id "$AMI_ID" \
        --count 1 \
        --instance-type "$INSTANCE_TYPE" \
        --key-name "$KEY_PAIR_NAME" \
        --security-groups "$SECURITY_GROUP_NAME" \
        --user-data file://user-data.sh \
        --region "$AWS_REGION" \
        --query 'Instances[0].InstanceId' \
        --output text)
    
    echo -e "${GREEN}✅ EC2 instance launched: ${INSTANCE_ID}${NC}"
    
    # Wait for instance to be running
    echo -e "${YELLOW}⏳ Waiting for instance to be running...${NC}"
    aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --region "$AWS_REGION"
    
    # Get public IP
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids "$INSTANCE_ID" \
        --region "$AWS_REGION" \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text)
    
    echo -e "${GREEN}✅ Instance is running${NC}"
    echo -e "${CYAN}🌐 Public IP: ${PUBLIC_IP}${NC}"
    
    # Cleanup
    rm -f user-data.sh
    
    # Show access information
    show_ec2_access_info "$PUBLIC_IP"
}

# Function to show EC2 access information
show_ec2_access_info() {
    local public_ip=$1
    
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo ""
    echo -e "${CYAN}📋 Access Information:${NC}"
    echo -e "  🖥️ SSH Access: ssh -i ${KEY_PAIR_NAME}.pem ec2-user@${public_ip}"
    echo -e "  🌐 Web App: http://${public_ip}:5000"
    echo -e "  📊 Analytics: http://${public_ip}:8501"
    echo -e "  ⚙️ Admin Panel: http://${public_ip}:8502"
    echo -e "  🔧 API Gateway: http://${public_ip}:8080"
    echo ""
    echo -e "${YELLOW}⚠️ Important Notes:${NC}"
    echo -e "  1. Services may take 5-10 minutes to fully start"
    echo -e "  2. Update .env file on the server with production values"
    echo -e "  3. Configure domain name and SSL for production use"
    echo -e "  4. Set up monitoring and backups"
    echo ""
    echo -e "${CYAN}🔧 Server Management:${NC}"
    echo -e "  📋 Check status: ssh -i ${KEY_PAIR_NAME}.pem ec2-user@${public_ip} 'docker ps'"
    echo -e "  📋 View logs: ssh -i ${KEY_PAIR_NAME}.pem ec2-user@${public_ip} 'cd dealer-dashboard && docker-compose logs'"
    echo -e "  🔄 Restart: ssh -i ${KEY_PAIR_NAME}.pem ec2-user@${public_ip} './start-dashboard.sh'"
    echo ""
}

# Function to create CloudFormation template
create_cloudformation_template() {
    echo -e "${YELLOW}📄 Creating CloudFormation template...${NC}"
    
    cat > dealer-dashboard-stack.yaml << 'EOF'
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Dealer Dashboard Infrastructure'

Parameters:
  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: EC2 Key Pair for SSH access
  
  InstanceType:
    Type: String
    Default: t3.large
    Description: EC2 instance type
  
  DomainName:
    Type: String
    Default: ""
    Description: Domain name for the application

Resources:
  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for Dealer Dashboard
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 5000
          ToPort: 5000
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 8000
          ToPort: 8000
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 8080
          ToPort: 8080
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 8501
          ToPort: 8502
          CidrIp: 0.0.0.0/0

  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0abcdef1234567890  # Update with latest Amazon Linux 2 AMI
      InstanceType: !Ref InstanceType
      KeyName: !Ref KeyPairName
      SecurityGroups:
        - !Ref SecurityGroup
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y docker git
          curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
          chmod +x /usr/local/bin/docker-compose
          systemctl start docker
          systemctl enable docker
          usermod -a -G docker ec2-user

Outputs:
  InstanceId:
    Description: Instance ID
    Value: !Ref EC2Instance
  
  PublicIP:
    Description: Public IP address
    Value: !GetAtt EC2Instance.PublicIp
  
  WebAppURL:
    Description: Web Application URL
    Value: !Sub 'http://${EC2Instance.PublicIp}:5000'
EOF
    
    echo -e "${GREEN}✅ CloudFormation template created: dealer-dashboard-stack.yaml${NC}"
}

# Function to show usage
show_usage() {
    echo -e "${CYAN}Usage: $0 [deployment_type]${NC}"
    echo ""
    echo -e "${YELLOW}Deployment Types:${NC}"
    echo -e "  ec2      - Deploy to EC2 instance (default)"
    echo -e "  ecs      - Deploy to ECS (coming soon)"
    echo -e "  fargate  - Deploy to Fargate (coming soon)"
    echo ""
    echo -e "${YELLOW}Environment Variables:${NC}"
    echo -e "  AWS_REGION        - AWS region (default: us-east-1)"
    echo -e "  KEY_PAIR_NAME     - EC2 key pair name"
    echo -e "  INSTANCE_TYPE     - EC2 instance type (default: t3.large)"
    echo -e "  DOMAIN_NAME       - Your domain name"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  $0 ec2"
    echo -e "  AWS_REGION=us-west-2 $0 ec2"
    echo -e "  INSTANCE_TYPE=t3.xlarge $0 ec2"
    echo ""
}

# Main execution
main() {
    case "$DEPLOYMENT_TYPE" in
        "ec2")
            check_aws_cli
            create_security_group
            create_key_pair
            deploy_ec2
            ;;
        "ecs"|"fargate")
            echo -e "${YELLOW}⚠️ ${DEPLOYMENT_TYPE} deployment coming soon${NC}"
            echo -e "${BLUE}💡 Use EC2 deployment for now: $0 ec2${NC}"
            exit 1
            ;;
        "help"|"-h"|"--help")
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown deployment type: ${DEPLOYMENT_TYPE}${NC}"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
