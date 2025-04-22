#!/bin/bash

# Kiểm tra tham số
if [ $# -ne 1 ]; then
    echo "Usage: ./switch_env.sh [dev|prod]"
    exit 1
fi

ENV_TYPE=$1

# Kiểm tra xem tham số có hợp lệ không
if [ "$ENV_TYPE" != "dev" ] && [ "$ENV_TYPE" != "prod" ]; then
    echo "Error: Environment type must be either 'dev' or 'prod'"
    exit 1
fi

# Kiểm tra xem file nguồn có tồn tại không
if [ ! -f ".env.$ENV_TYPE" ]; then
    echo "Error: Source file .env.$ENV_TYPE does not exist"
    exit 1
fi

# Sao chép file
cp ".env.$ENV_TYPE" .env

# Kiểm tra kết quả
if [ $? -eq 0 ]; then
    echo "Successfully switched to $ENV_TYPE environment"
    exit 0
else
    echo "Error switching environment"
    exit 1
fi 