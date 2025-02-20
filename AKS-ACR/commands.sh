#!/bin/bash

# Variables
MYACR=ajdemo
RG=aj-rg
REGION=centralindia

# Cpmmands 
az group create -n $RG -l $REGION && az acr create --name $MYACR --resource-group $RG --sku basic
az acr create --name $MYACR --resource-group $RG --sku basic
az aks create --name myAKSCluster --resource-group $RG --generate-ssh-keys --attach-acr $MYACR

# Login
az acr import --name $MYACR --source docker.io/library/nginx:latest --image nginx:v1
# or docker build -t oj09/image:tag .
az aks get-credentials --resource-group $RG --name myAKSCluster

# CReate
sed -i "s/acr/$MYACR/g" deployment.yaml 
kubectl apply -f deployment.yaml
