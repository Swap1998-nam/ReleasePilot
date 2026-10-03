# Java 21 + deps 
sudo apt-get update
sudo apt-get install -y fontconfig openjdk-21-jre

# Jenkins LTS repo (2026 signing key)
sudo mkdir -p /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key
echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" \
  | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

# Install and start
sudo apt-get update
sudo apt-get install -y jenkins
sudo systemctl enable --now jenkins
systemctl status jenkins --no-pager

# Initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
