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

This phase sets up the backend infrastructure for the TravelMemory MERN app using AWS EC2 and Python automation.

### 📾 Steps Performed

- ✅ cd into phase1-backend directory and run python script to Create a backend key pair using:
  ```bash
  python create-ec2-key-pair.py
  ```

- ✅ Launch a backend EC2 instance:
  ```bash
  python Backend-ec2-instance-elastic-ip.py
  ```

- ✅ Python script will:
  - Launch the instance
  - Automatically assign an **Elastic IP**
  - Generate a shell script `setup-server.sh` for provisioning

- ✅ SSH and configure the instance:
  ```bash
  sudo ./setup-server.sh
  ```

- ✅ SSH into the instance using the private key and do the following:

  1. **Clone the repository**:
     ```bash
     git clone https://github.com/UnpredictablePrashant/TravelMemory.git
     cd TravelMemory/backend
     ```

  2. **Configure environment variables**:
     ```bash
     sudo nano .env
     ```

     Add the following:
     ```env
     MONGO_URI=<your MongoDB URI>
     PORT=3000
     ```

  3. **Install dependencies & start the backend server**:
     ```bash
     npm install
     node index.js
     ```

---

### 🔎 Backend API Testing

Once the server is running, test it using:

🌐 `http://<backend EC2 instance Public Ip>:3000/trip`


---

## ✅ Phase 2 – Frontend EC2 Instance Setup

This phase sets up the frontend infrastructure for the TravelMemory MERN app using AWS EC2 and Python automation.

### 📖 Steps Performed

- ✅ Navigate to the `phase2-frontend/` directory and create a frontend key pair:
  ```bash
  python create-ec2-key-pair.py
  ```

- ✅ Launch a frontend EC2 instance:
  ```bash
  python Frontend-ec2-instance-elastic-ip.py
  ```

- ✅ Python script will:
  - Launch the instance
  - Automatically assign an **Elastic IP**
  - Generate a shell script `setup-server.sh` for provisioning

- ✅ SSH and configure the instance:
  ```bash
  sudo ./setup-server.sh
  ```

- ✅ SSH into the instance using the private key and do the following:

  1. **Clone the repository**:
     ```bash
     git clone https://github.com/UnpredictablePrashant/TravelMemory.git
     cd TravelMemory/frontend
     ```

  2. **Update the frontend base URL**:
     ```bash
     nano src/url.js
     ```
     Add:
     ```js
     export const baseUrl = process.env.REACT_APP_BACKEND_URL || "http://<backend EC2 instance Public Ip>:3000";
     ```

  3. **Install dependencies**:
     ```bash
     npm install
     ```

  4. **Start the frontend server for testing**:
     ```bash
     npm start
     ```
     Test on:
     
     🌐 `http://<frontend EC2 instance Public Ip>:3000`


---

## ✅ Phase 3 – Setup NGINX Proxy for Production

- Build the frontend:
  ```bash
  npm run build
  ```

- Copy the build to NGINX public directory:
  ```bash
  sudo cp -r build/* /var/www/html/
  ```

- Test and restart NGINX:
  ```bash
  sudo nginx -t
  sudo systemctl restart nginx
  ```

- Access your React app via:
  
  🌐 `http://3.109.71.149/`

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
