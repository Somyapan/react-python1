# AWS Infrastructure Setup Guide

This guide walks you through setting up all AWS resources for your application deployment with:
- **ECR** (Elastic Container Registry) for Docker images
- **ECS** (Elastic Container Service) for running containers
- **ALB** (Application Load Balancer) for traffic distribution
- **ACM** (AWS Certificate Manager) for SSL/HTTPS
- **Route 53** for DNS routing
- **RDS** for MySQL database

---

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** installed (optional, but recommended)
3. **AWS CLI** configured with credentials
4. **Domain name** (for HTTPS setup)
5. **RDS MySQL instance** already created

---

## Step 1: Request SSL Certificate (ACM)

### Via AWS Console:
1. Go to **AWS Certificate Manager (ACM)**
2. Click **Request a certificate**
3. Choose **Request a public certificate**
4. Enter your domain:
   - Primary domain: `yourdomain.com`
   - Add alternative: `*.yourdomain.com`
5. Choose **DNS validation** (recommended)
6. Complete DNS validation by adding CNAME records to your DNS provider
7. **Copy the Certificate ARN** (you'll need this for Terraform)

---

## Step 2: Create ECR Repositories

### Option A: Using Terraform (Recommended)

1. Copy `terraform.tfvars.example` to `terraform.tfvars`
2. Update all values in `terraform.tfvars`:
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   ```
3. Edit `terraform.tfvars` with your actual values:
   ```hcl
   domain_name         = "yourdomain.com"
   acm_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/..."
   rds_host            = "your-rds-endpoint.rds.amazonaws.com"
   rds_user            = "admin"
   rds_password        = "your-secure-password"
   ```
4. Initialize Terraform:
   ```bash
   terraform init
   ```
5. Review the plan:
   ```bash
   terraform plan
   ```
6. Apply the configuration:
   ```bash
   terraform apply
   ```
7. Note the outputs (ALB DNS, ECR URLs, etc.)

### Option B: Using AWS Console (Manual)

#### Create Backend ECR Repository:
1. Go to **Amazon ECR** → **Repositories**
2. Click **Create repository**
3. Name: `student-form-app-backend`
4. Enable **image scanning on push**
5. Click **Create repository**
6. Note the **repository URI**

#### Create Frontend ECR Repository:
1. Click **Create repository**
2. Name: `student-form-app-frontend`
3. Enable **image scanning on push**
4. Click **Create repository**
5. Note the **repository URI**

---

## Step 3: Push Docker Images to ECR

1. Authenticate with ECR:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
   ```

2. Build and push backend image:
   ```bash
   docker build -t student-form-app-backend ./backend
   docker tag student-form-app-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/student-form-app-backend:latest
   docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/student-form-app-backend:latest
   ```

3. Build and push frontend image:
   ```bash
   docker build -t student-form-app-frontend ./frontend
   docker tag student-form-app-frontend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/student-form-app-frontend:latest
   docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/student-form-app-frontend:latest
   ```

---

## Step 4: Set Up GitHub Actions Secrets

Add these secrets to your GitHub repository (Settings → Secrets):

- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- `RDS_HOST` - RDS MySQL endpoint
- `RDS_PORT` - `3306`
- `RDS_USER` - RDS username
- `RDS_PASSWORD` - RDS password
- `RDS_DB` - Database name (`studentdb`)

---

## Step 5: Update DNS Records (Route 53 or External DNS)

If using Terraform with `create_route53_record = true`:
- This is automated (ensure you have a Route 53 hosted zone)

If using external DNS provider:
1. Get the **ALB DNS name** from Terraform output or AWS Console:
   ```bash
   terraform output alb_dns_name
   ```
2. Create an **A record** pointing to the ALB:
   - Name: `yourdomain.com`
   - Type: `A` (or `ALIAS` if supported)
   - Value: `student-form-app-alb-xxx.us-east-1.elb.amazonaws.com`
3. Wait for DNS propagation (can take 15-30 minutes)

---

## Step 6: Verify the Setup

### Test the Application:
1. Wait 2-3 minutes for ECS tasks to start
2. Open your browser and go to `https://yourdomain.com`
3. You should see your frontend application
4. API calls to `https://yourdomain.com/api/*` will be routed to the backend

### Check Health:
1. Backend health: `https://yourdomain.com/health`
2. API docs: `https://yourdomain.com/docs`

### View Logs:
```bash
# Backend logs
aws logs tail /ecs/student-form-app-backend --follow

# Frontend logs
aws logs tail /ecs/student-form-app-frontend --follow
```

---

## Step 7: Auto-Deployment with GitHub Actions

Now, every time you push to the `main` branch:
1. GitHub Actions builds the Docker images
2. Pushes to ECR
3. Updates ECS task definitions
4. Deploys to ECS services

No manual deployment needed!

---

## Troubleshooting

### 1. ALB shows unhealthy targets
- Check ECS task logs
- Verify security group allows ALB → ECS communication
- Ensure backend is listening on port 8000
- Ensure frontend is listening on port 5173

### 2. HTTPS not working
- Verify ACM certificate is valid
- Check ALB listener configuration
- Ensure domain DNS is pointing to ALB

### 3. Frontend can't reach backend
- Check `VITE_API_BASE_URL` environment variable
- Verify ALB listener rules for `/api/*` path
- Check backend target group health checks

### 4. Docker images not updating
- Ensure GitHub Actions secrets are set
- Check GitHub Actions workflow logs
- Verify ECR credentials in GitHub Actions

---

## Cost Optimization

### To reduce costs:
1. **Reduce desired count:**
   - Change `desired_count` in ECS services from 2 to 1
   - Modify in `terraform/main.tf`

2. **Use FARGATE_SPOT:**
   - Change launch type to `FARGATE_SPOT` (70% cheaper)
   - Less suitable for production

3. **Remove unused resources:**
   - Delete ALB if not needed
   - Scale down ECS tasks during off-hours

---

## Next Steps

1. ✅ Create ECR repositories
2. ✅ Request ACM certificate
3. ✅ Run Terraform to create all resources
4. ✅ Push Docker images to ECR
5. ✅ Set up GitHub Actions secrets
6. ✅ Configure DNS records
7. ✅ Test the application
8. ✅ Monitor logs and performance

---

## Resources

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS Certificate Manager](https://docs.aws.amazon.com/acm/)
- [AWS Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/)
