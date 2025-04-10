#!/bin/bash
# Setup script for Ubuntu server
echo "Setting up your Travel Memory application server..."

# Connect to the server
ssh -i "TMKeyPrinceBackend.pem" ubuntu@13.203.123.95 '
    # Update package lists
    sudo apt update
    
    # Install Node.js (using NodeSource for more recent version)
    echo "Installing Node.js and npm..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
    
    # Install MongoDB
    echo "Installing MongoDB..."
    sudo apt install -y mongodb
    sudo systemctl start mongodb
    sudo systemctl enable mongodb
    
    # Install Nginx
    echo "Installing Nginx..."
    sudo apt install -y nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    # Install git
    echo "Installing git..."
    sudo apt install -y git
    
    # Create application directory
    echo "Setting up application directory..."
    mkdir -p ~/travel-memory-app
    
    # Check versions
    echo "Installed versions:"
    echo "Node.js: $(node -v)"
    echo "npm: $(npm -v)"
    echo "MongoDB: $(mongod --version | head -n 1)"
    echo "Nginx: $(nginx -v 2>&1)"
    echo "Git: $(git --version)"
    
    echo "Setup complete!"
'
