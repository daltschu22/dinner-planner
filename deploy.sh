#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Family Dinner Planner - Vercel Deployment Script${NC}"
echo "======================================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}Error: Vercel CLI is not installed.${NC}"
    echo "Please install it using: npm install -g vercel"
    exit 1
fi

# Check if user is logged in to Vercel
echo -e "${YELLOW}Checking Vercel login status...${NC}"
vercel whoami &> /dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}You need to log in to Vercel first.${NC}"
    vercel login
fi

# Deployment options
echo -e "${YELLOW}Select deployment option:${NC}"
echo "1) Deploy to preview (development)"
echo "2) Deploy to production"
echo "3) Set environment variables"
echo "4) Exit"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo -e "${YELLOW}Deploying to preview environment...${NC}"
        vercel
        ;;
    2)
        echo -e "${YELLOW}Deploying to production environment...${NC}"
        vercel --prod
        ;;
    3)
        echo -e "${YELLOW}Setting environment variables...${NC}"
        echo "Which environment variable would you like to set?"
        echo "1) REDIS_URL"
        echo "2) SECRET_KEY"
        echo "3) Custom variable"
        
        read -p "Enter your choice (1-3): " var_choice
        
        case $var_choice in
            1)
                read -p "Enter your Redis URL: " redis_url
                vercel env add REDIS_URL production
                ;;
            2)
                read -p "Enter your secret key (or press enter to generate one): " secret_key
                if [ -z "$secret_key" ]; then
                    # Generate a random secret key
                    secret_key=$(python -c "import secrets; print(secrets.token_hex(32))")
                    echo -e "${GREEN}Generated secret key: ${secret_key}${NC}"
                fi
                vercel env add SECRET_KEY production
                ;;
            3)
                read -p "Enter variable name: " var_name
                read -p "Enter variable value: " var_value
                read -p "Environment (development/preview/production): " env_type
                vercel env add $var_name $env_type
                ;;
            *)
                echo -e "${RED}Invalid choice.${NC}"
                ;;
        esac
        ;;
    4)
        echo -e "${GREEN}Exiting.${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice.${NC}"
        ;;
esac

echo -e "${GREEN}Done!${NC}" 
