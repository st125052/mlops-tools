#!/bin/bash
yum update -y
yum install -y git
yum install -y docker
mkdir -p /usr/local/lib/docker/cli-plugins
curl -fL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
curl -fL https://github.com/docker/buildx/releases/download/v0.17.1/buildx-v0.17.1.linux-amd64 \
  -o /usr/local/lib/docker/cli-plugins/docker-buildx
chmod +x /usr/local/lib/docker/cli-plugins/docker-buildx
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user
systemctl restart docker