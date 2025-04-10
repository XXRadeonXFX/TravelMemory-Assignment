# TravelMemory MERN Application Deployment – AWS Infrastructure

This project demonstrates the full deployment lifecycle of a MERN (MongoDB, Express, React, Node.js) application called **TravelMemory**, automated and scaled on AWS using Python, Shell, and Boto3.

---

## 📁 Project Structure

```
TravelMemory-Assignment/
├── phase1-backend/                  # Backend EC2 setup and provisioning
├── phase2-frontend/                 # Frontend EC2 setup and provisioning
├── phase3-nginx-frontend-config/   # NGINX configuration for React app
├── phase4-scaling-instances/       # Auto-scaling logic using Boto3
├── phase5-add-load-balancer/       # Load Balancer + Target Group setup
├── phase6-add-domain-cloudflare/   # Domain mapping via Cloudflare
└── Travel Memory Documentation.docx
```

---

## ✅ Phase 1 – Backend EC2 Instance Setup

Scripts and files to:
- Create a key pair
- Launch a backend EC2 instance
- Attach an Elastic IP
- Configure Node.js/Express and connect to MongoDB

Files:
- `create-ec2-key-pair.py`
- `Backend-ec2-instance-elastic-ip.py`
- `setup-server.sh`

---

## ✅ Phase 2 – Frontend EC2 Instance Setup

Scripts and files to:
- Deploy React frontend
- Serve app using NGINX
- Assign static Elastic IP

Files:
- `create-ec2-key-pair.py`
- `Frontend-ec2-instance-elastic-ip.py`
- `setup-server.sh`

---

## ✅ Phase 3 – NGINX Configuration

Includes:
- `nginx-frontend-config.txt` for NGINX reverse proxy
- Auto-start React build for production environment

---

## ✅ Phase 4 – Instance Scaling

Python script using Boto3 to:
- Scale out EC2 instances (frontend/backend)
- Tag and configure instances for scalability

Files:
- `autoscaling-instances.py`
- `autoscale-readme.txt`

---

## ✅ Phase 5 – Load Balancer Integration

Python automation to:
- Create an Application Load Balancer (ALB)
- Register multiple frontend EC2 instances as targets
- Health check integration and listener setup

File:
- `Adding-LOAD-Balancer.py`

---

## ✅ Phase 6 – Domain Mapping with Cloudflare

Scripts (coming soon or manually configured) to:
- Point a custom domain (e.g., travelmemory.yourdomain.com) to the ALB via Cloudflare
- Create A and CNAME records
- Handle SSL settings

---

## 🧪 Tech Stack Used

- **AWS EC2, VPC, Subnets, ALB, EIPs**
- **Python 3.10+ (Boto3 for AWS SDK)**
- **Bash scripting**
- **React + Node.js**
- **NGINX**
- **MongoDB Atlas**
- **Cloudflare DNS**
- **IAM Key & Role Configurations**

---

## 📝 How to Run

> Make sure AWS CLI is configured (`aws configure`) and Python `boto3` is installed.

```bash
pip install boto3
cd phase1-backend/
python create-ec2-key-pair.py
python Backend-ec2-instance-elastic-ip.py
# Repeat similar for frontend & subsequent phases
```

Each phase builds on the previous one. Refer to the documentation for screenshots and detailed walkthroughs.

---

## 📄 Documentation

Full deployment steps, architecture diagram, IP configurations, and screenshots can be found in:

- `Travel Memory Documentation.docx`

---

## 🧠 Contributors

👨‍💻 Prince Thakur  
🔧 DevOps & Cloud Automation – DXC Technology  
📧 [Add email/LinkedIn if required]

---
