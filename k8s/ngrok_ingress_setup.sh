#!/bin/bash

# Exit on any error
set -e

# Check for required environment variables
if [ -z "$NGROK_AUTHTOKEN" ] || [ -z "$NGROK_API_KEY" ]; then
    echo "Error: NGROK_AUTHTOKEN and NGROK_API_KEY must be set"
    echo "Please export these variables:"
    echo "export NGROK_AUTHTOKEN=your_authtoken"
    echo "export NGROK_API_KEY=your_api_key"
    exit 1
fi

# Add the ngrok Helm repository
echo "Adding ngrok Helm repository..."
helm repo add ngrok https://charts.ngrok.com
helm repo update

# Install the ngrok controller
echo "Installing ngrok ingress controller..."
helm install ngrok-ingress-controller ngrok/kubernetes-ingress-controller \
  --namespace ngrok-ingress-controller \
  --create-namespace \
  --set credentials.apiKey=$NGROK_API_KEY \
  --set credentials.authtoken=$NGROK_AUTHTOKEN

# Wait for the controller to be ready
echo "Waiting for ngrok controller to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kubernetes-ingress-controller -n ngrok-ingress-controller --timeout=90s

echo "Setup complete! You can now create Ingress resources using the ngrok class."
echo "Example usage:"
echo "kubectl apply -f ingress.yaml"