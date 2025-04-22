import os
import shutil
import sys

def switch_environment(env_type):
    """
    Switch between development and production environment files
    """
    env_files = {
        'dev': '.env.dev',
        'prod': '.env.prod'
    }
    
    if env_type not in env_files:
        print(f"Error: Environment type must be either 'dev' or 'prod'")
        return False
    
    source_file = env_files[env_type]
    target_file = '.env'
    
    if not os.path.exists(source_file):
        print(f"Error: Source file {source_file} does not exist")
        return False
    
    try:
        # Copy the environment file
        shutil.copy2(source_file, target_file)
        print(f"Successfully switched to {env_type} environment")
        return True
    except Exception as e:
        print(f"Error switching environment: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python switch_env.py [dev|prod]")
        sys.exit(1)
    
    env_type = sys.argv[1].lower()
    success = switch_environment(env_type)
    sys.exit(0 if success else 1) 