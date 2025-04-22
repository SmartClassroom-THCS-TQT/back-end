#!/bin/bash

# Tìm thư mục back-end từ thư mục home
BACKEND_DIR="$HOME/back-end"

# Kiểm tra xem thư mục back-end có tồn tại không
if [ ! -d "$BACKEND_DIR" ]; then
    echo "Error: Backend directory not found at $BACKEND_DIR"
    exit 1
fi

# Kiểm tra tham số
if [ $# -ne 1 ]; then
    echo "Usage: switch_env.sh [dev|prod]"
    exit 1
fi

ENV_TYPE=$1

# Kiểm tra xem tham số có hợp lệ không
if [ "$ENV_TYPE" != "dev" ] && [ "$ENV_TYPE" != "prod" ]; then
    echo "Error: Environment type must be either 'dev' or 'prod'"
    exit 1
fi

# Đường dẫn đầy đủ của các file
SOURCE_FILE="$BACKEND_DIR/.env.$ENV_TYPE"
TARGET_FILE="$BACKEND_DIR/.env"

# Kiểm tra xem file nguồn có tồn tại không
if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: Source file $SOURCE_FILE does not exist"
    exit 1
fi

# In thông tin debug
echo "Backend directory: $BACKEND_DIR"
echo "Source file: $SOURCE_FILE"
echo "Target file: $TARGET_FILE"

# Sao chép file
cp "$SOURCE_FILE" "$TARGET_FILE"

# Kiểm tra kết quả
if [ $? -eq 0 ]; then
    # Kiểm tra xem file đích có tồn tại và có nội dung không
    if [ -f "$TARGET_FILE" ] && [ -s "$TARGET_FILE" ]; then
        echo "Successfully switched to $ENV_TYPE environment"
        echo "File content:"
        cat "$TARGET_FILE"
        exit 0
    else
        echo "Error: Target file was not created or is empty"
        exit 1
    fi
else
    echo "Error switching environment"
    exit 1
fi 