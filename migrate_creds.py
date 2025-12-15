#!/usr/bin/env python3
"""
Migrate credentials from local_settings.cfg to ~/.archivessnake.yml

This script reads credentials from the old local_settings.cfg file
and creates the new archivessnake and asinventory configuration files.
"""

import os
import sys
import configparser
import yaml

def main():
    # Determine script location (works with both .py and .exe)
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller bundle
        script_dir = os.path.dirname(sys.executable)
    else:
        # Running as a normal Python script
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to old config file
    config_path = os.path.join(script_dir, "local_settings.cfg")
    
    if not os.path.isfile(config_path):
        print(f"ERROR: Could not find local_settings.cfg in {script_dir}")
        print("\nExpected location:", config_path)
        input("\nPress Enter to exit...")
        return
    
    # Read old config
    print(f"Reading credentials from: {config_path}")
    config = configparser.ConfigParser()
    config.read(config_path)
    
    try:
        baseurl = config.get('ArchivesSpace', 'baseURL')
        repository = config.get('ArchivesSpace', 'repository')
        username = config.get('ArchivesSpace', 'user')
        password = config.get('ArchivesSpace', 'password')
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        print(f"ERROR: Missing required setting in local_settings.cfg: {e}")
        input("\nPress Enter to exit...")
        return
    
    # Create ~/.archivessnake.yml for credentials
    archivessnake_path = os.path.join(os.path.expanduser('~'), '.archivessnake.yml')
    archivessnake_config = {
        'baseurl': baseurl,
        'username': username,
        'password': password
    }
    
    # Check if archivessnake config already exists
    if os.path.isfile(archivessnake_path):
        print(f"\nWARNING: {archivessnake_path} already exists!")
        response = input("Overwrite? (y/n): ")
        if response.lower() not in ['y', 'yes']:
            print("Skipping archivessnake configuration...")
        else:
            with open(archivessnake_path, 'w') as f:
                yaml.dump(archivessnake_config, f, default_flow_style=False)
            print(f"✓ Created: {archivessnake_path}")
    else:
        with open(archivessnake_path, 'w') as f:
            yaml.dump(archivessnake_config, f, default_flow_style=False)
        print(f"✓ Created: {archivessnake_path}")
    
    # Create ~/asinventory.yml for repository ID
    asinventory_path = os.path.join(os.path.expanduser('~'), 'asinventory.yml')
    asinventory_config = {
        'repository': repository
    }
    
    
    print("\n" + "="*60)
    print("Migration complete!")
    print("="*60)
    print("\nConfiguration files created:")
    print(f"  • {archivessnake_path}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
