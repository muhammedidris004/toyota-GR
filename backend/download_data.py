#!/usr/bin/env python3
"""
Data Download Script for GR Race Strategist AI

This script downloads the Data-GR folder from cloud storage.
Supports multiple cloud providers: Google Drive, AWS S3, Dropbox, Kaggle, etc.

IMPORTANT: This downloads data to local disk for fast access.
The backend code reads from local files (backend/Data-GR/) for optimal performance.

Usage:
    python download_data.py --provider kaggle --dataset <username/dataset-name>
    python download_data.py --provider gdrive --url <share_link>
    python download_data.py --provider s3 --bucket <bucket> --key <key>
    python download_data.py --provider dropbox --url <share_link>

Why Download Instead of Streaming?
- Fast access: Local disk is much faster than network
- ML processing: Models need to read data multiple times
- Reliability: No network timeouts during processing
- Standard practice: Most ML projects download data once
"""

import argparse
import os
import sys
import zipfile
import shutil
from pathlib import Path
from typing import Optional

try:
    import requests
    from tqdm import tqdm
except ImportError:
    print("❌ Missing required packages. Installing...")
    os.system(f"{sys.executable} -m pip install requests tqdm")
    import requests
    from tqdm import tqdm

try:
    import kaggle
except ImportError:
    kaggle = None


def download_file(url: str, output_path: Path, description: str = "Downloading"):
    """Download a file with progress bar"""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(output_path, 'wb') as f, tqdm(
        desc=description,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))


def download_from_google_drive(share_url: str, output_dir: Path):
    """Download from Google Drive share link"""
    print("📥 Downloading from Google Drive...")
    
    # Extract file ID from Google Drive URL
    file_id = None
    if 'id=' in share_url:
        file_id = share_url.split('id=')[1].split('&')[0]
    elif '/d/' in share_url:
        file_id = share_url.split('/d/')[1].split('/')[0]
    
    if not file_id:
        raise ValueError("Invalid Google Drive URL. Please provide a shareable link.")
    
    # Google Drive direct download URL
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    # First request to get confirmation for large files
    response = requests.get(download_url, stream=True)
    if 'virus scan warning' in response.text.lower():
        # Extract confirmation token
        import re
        match = re.search(r'confirm=([^&]+)', response.text)
        if match:
            confirm_token = match.group(1)
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={confirm_token}"
    
    zip_path = output_dir / "Data-GR.zip"
    download_file(download_url, zip_path, "Downloading Data-GR.zip")
    
    print("📦 Extracting archive...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    
    zip_path.unlink()  # Remove zip file
    print("✅ Data downloaded and extracted successfully!")


def download_from_dropbox(share_url: str, output_dir: Path):
    """Download from Dropbox share link"""
    print("📥 Downloading from Dropbox...")
    
    # Convert Dropbox share link to direct download
    if '?dl=0' in share_url:
        download_url = share_url.replace('?dl=0', '?dl=1')
    elif '?dl=1' not in share_url:
        download_url = f"{share_url}?dl=1"
    else:
        download_url = share_url
    
    zip_path = output_dir / "Data-GR.zip"
    download_file(download_url, zip_path, "Downloading Data-GR.zip")
    
    print("📦 Extracting archive...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    
    zip_path.unlink()
    print("✅ Data downloaded and extracted successfully!")


def download_from_s3(bucket: str, key: str, output_dir: Path, aws_access_key: Optional[str] = None, aws_secret_key: Optional[str] = None):
    """Download from AWS S3"""
    print("📥 Downloading from AWS S3...")
    
    try:
        import boto3
    except ImportError:
        print("Installing boto3...")
        os.system(f"{sys.executable} -m pip install boto3")
        import boto3
    
    # Create S3 client
    if aws_access_key and aws_secret_key:
        s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    else:
        # Use default credentials from ~/.aws/credentials or environment
        s3_client = boto3.client('s3')
    
    zip_path = output_dir / "Data-GR.zip"
    
    print(f"Downloading s3://{bucket}/{key}...")
    s3_client.download_file(bucket, key, str(zip_path))
    
    print("📦 Extracting archive...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    
    zip_path.unlink()
    print("✅ Data downloaded and extracted successfully!")


def download_from_url(direct_url: str, output_dir: Path):
    """Download from direct URL"""
    print("📥 Downloading from direct URL...")
    
    zip_path = output_dir / "Data-GR.zip"
    download_file(direct_url, zip_path, "Downloading Data-GR.zip")
    
    print("📦 Extracting archive...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    
    zip_path.unlink()
    print("✅ Data downloaded and extracted successfully!")


def download_from_kaggle(dataset: str, output_dir: Path, unzip: bool = True):
    """
    Download from Kaggle dataset
    
    Args:
        dataset: Kaggle dataset in format "username/dataset-name" (e.g., "muhammedidris/toyota-gr-data")
        output_dir: Directory to download to
        unzip: Whether to automatically extract zip files
    """
    print("📥 Downloading from Kaggle...")
    
    if kaggle is None:
        print("Installing kaggle package...")
        os.system(f"{sys.executable} -m pip install kaggle")
        import kaggle
    
    # Check for Kaggle API credentials
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if not kaggle_json.exists():
        print("\n⚠️  Kaggle API credentials not found!")
        print("To download from Kaggle, you need to:")
        print("1. Go to https://www.kaggle.com/settings")
        print("2. Scroll to 'API' section")
        print("3. Click 'Create New Token' - this downloads kaggle.json")
        print("4. Place kaggle.json in ~/.kaggle/ directory")
        print("5. Set permissions: chmod 600 ~/.kaggle/kaggle.json")
        print("\nAlternatively, you can download manually from the Kaggle dataset page.")
        raise FileNotFoundError("Kaggle API credentials not found. See instructions above.")
    
    # Set output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading dataset: {dataset}")
    print(f"Output directory: {output_dir}")
    
    try:
        # Download dataset
        kaggle.api.dataset_download_files(
            dataset,
            path=str(output_dir),
            unzip=unzip
        )
        
        if unzip:
            print("✅ Data downloaded and extracted successfully!")
        else:
            # If not auto-unzipped, extract manually
            zip_files = list(output_dir.glob("*.zip"))
            if zip_files:
                print("📦 Extracting archive...")
                for zip_file in zip_files:
                    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                        zip_ref.extractall(output_dir)
                    zip_file.unlink()
                print("✅ Data downloaded and extracted successfully!")
            else:
                print("✅ Data downloaded successfully!")
                
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            print("\n❌ Authentication failed!")
            print("Please check your Kaggle API credentials in ~/.kaggle/kaggle.json")
        elif "404" in error_msg or "not found" in error_msg.lower():
            print(f"\n❌ Dataset not found: {dataset}")
            print("Please check the dataset name format: username/dataset-name")
            print("Example: muhammedidris/toyota-gr-data")
        else:
            print(f"\n❌ Error downloading from Kaggle: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description='Download Data-GR folder from cloud storage')
    parser.add_argument('--provider', choices=['gdrive', 'dropbox', 's3', 'url', 'kaggle'], 
                       required=True, help='Cloud storage provider')
    parser.add_argument('--url', help='Share URL (for gdrive, dropbox, or url)')
    parser.add_argument('--dataset', help='Kaggle dataset name in format username/dataset-name (for kaggle provider)')
    parser.add_argument('--bucket', help='S3 bucket name (for s3 provider)')
    parser.add_argument('--key', help='S3 object key (for s3 provider)')
    parser.add_argument('--aws-key', help='AWS access key (optional, for s3)')
    parser.add_argument('--aws-secret', help='AWS secret key (optional, for s3)')
    parser.add_argument('--output', default='.', help='Output directory (default: current directory)')
    parser.add_argument('--no-unzip', action='store_true', help='Do not auto-extract (for kaggle)')
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    data_dir = output_dir / "backend" / "Data-GR"
    
    # Check if data already exists
    if data_dir.exists() and any(data_dir.iterdir()):
        response = input(f"⚠️  Data-GR already exists at {data_dir}. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Download cancelled.")
            return
        shutil.rmtree(data_dir)
    
    # Create output directory
    data_dir.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if args.provider == 'gdrive':
            if not args.url:
                print("❌ --url required for Google Drive")
                return
            download_from_google_drive(args.url, output_dir / "backend")
        
        elif args.provider == 'dropbox':
            if not args.url:
                print("❌ --url required for Dropbox")
                return
            download_from_dropbox(args.url, output_dir / "backend")
        
        elif args.provider == 's3':
            if not args.bucket or not args.key:
                print("❌ --bucket and --key required for S3")
                return
            download_from_s3(args.bucket, args.key, output_dir / "backend", args.aws_key, args.aws_secret)
        
        elif args.provider == 'url':
            if not args.url:
                print("❌ --url required for direct URL")
                return
            download_from_url(args.url, output_dir / "backend")
        
        elif args.provider == 'kaggle':
            if not args.dataset:
                print("❌ --dataset required for Kaggle")
                print("   Format: username/dataset-name")
                print("   Example: muhammedidris/toyota-gr-data")
                return
            download_from_kaggle(args.dataset, output_dir / "backend", unzip=not args.no_unzip)
        
        print(f"\n✅ Data-GR downloaded successfully to {data_dir}")
        print(f"📁 Size: {sum(f.stat().st_size for f in data_dir.rglob('*') if f.is_file()) / (1024**3):.2f} GB")
        
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

