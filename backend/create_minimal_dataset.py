#!/usr/bin/env python3
"""
Create Minimal Dataset for GitHub

This script creates a minimal Data-GR dataset with only essential files:
- Analysis files (*23_AnalysisEnduranceWithSections*)
- Results files (*Results*.CSV)
- Lap time files (*lap_time*.csv, *lap_start*.csv, *lap_end*.csv)

EXCLUDES:
- Telemetry files (*telemetry*.csv) - These are 1-3GB each and NOT used by the app
- Weather files (optional)
- Other large files

Target: Keep total size under 50MB for GitHub
"""

import shutil
from pathlib import Path
import sys

def get_file_size_mb(file_path: Path) -> float:
    """Get file size in MB"""
    return file_path.stat().st_size / (1024 * 1024)

def create_minimal_dataset(source_dir: Path, output_dir: Path, max_size_mb: float = 50.0):
    """
    Create minimal dataset with only essential files
    
    Args:
        source_dir: Source Data-GR directory
        output_dir: Output directory for minimal dataset
        max_size_mb: Maximum total size in MB (default: 50MB for GitHub)
    """
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)
    
    # Essential file patterns (these are what the app actually uses)
    essential_patterns = [
        "*23_AnalysisEnduranceWithSections*",  # Main analysis files
        "*Results*.CSV",                        # Results files
        "*Results*.csv",                        # Results files (lowercase)
        "*lap_time*.csv",                       # Lap time files
        "*lap_start*.csv",                      # Lap start files
        "*lap_end*.csv",                        # Lap end files
    ]
    
    # Exclude patterns (large files not used by app)
    exclude_patterns = [
        "*telemetry*.csv",                      # HUGE files (1-3GB each) - NOT USED
        "*telemetry*.CSV",
    ]
    
    print(f"📁 Source: {source_dir}")
    print(f"📁 Output: {output_dir}")
    print(f"📊 Max size: {max_size_mb} MB\n")
    
    # Find all essential files
    essential_files = []
    total_size = 0.0
    
    print("🔍 Scanning for essential files...")
    for pattern in essential_patterns:
        files = list(source_dir.rglob(pattern))
        for file in files:
            # Check if file matches exclude patterns
            should_exclude = False
            for exclude_pattern in exclude_patterns:
                if file.match(exclude_pattern):
                    should_exclude = True
                    break
            
            if not should_exclude and file.is_file():
                size_mb = get_file_size_mb(file)
                essential_files.append((file, size_mb))
                total_size += size_mb
    
    # Sort by size (smallest first) to prioritize keeping more files
    essential_files.sort(key=lambda x: x[1])
    
    print(f"✅ Found {len(essential_files)} essential files")
    print(f"📊 Total size: {total_size:.2f} MB\n")
    
    if total_size > max_size_mb:
        print(f"⚠️  Total size ({total_size:.2f} MB) exceeds limit ({max_size_mb} MB)")
        print("📋 Selecting files to fit within limit...\n")
        
        # Select files that fit within limit
        selected_files = []
        current_size = 0.0
        
        for file, size_mb in essential_files:
            if current_size + size_mb <= max_size_mb:
                selected_files.append((file, size_mb))
                current_size += size_mb
            else:
                print(f"⏭️  Skipping {file.name} ({size_mb:.2f} MB) - would exceed limit")
        
        essential_files = selected_files
        total_size = current_size
        print(f"\n✅ Selected {len(essential_files)} files ({total_size:.2f} MB)\n")
    
    # Create output directory structure
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files maintaining directory structure
    print("📦 Copying files...")
    copied_count = 0
    
    for source_file, size_mb in essential_files:
        # Get relative path from source_dir
        relative_path = source_file.relative_to(source_dir)
        dest_file = output_dir / relative_path
        
        # Create parent directories
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(source_file, dest_file)
        copied_count += 1
        
        if copied_count % 10 == 0:
            print(f"  Copied {copied_count}/{len(essential_files)} files...")
    
    print(f"\n✅ Copied {copied_count} files")
    print(f"📊 Total size: {total_size:.2f} MB")
    print(f"📁 Output location: {output_dir}")
    
    # Verify by checking one track
    print("\n🔍 Verifying structure...")
    tracks = [d for d in output_dir.iterdir() if d.is_dir()]
    if tracks:
        print(f"✅ Found {len(tracks)} tracks: {', '.join([t.name for t in tracks[:5]])}")
        if len(tracks) > 5:
            print(f"   ... and {len(tracks) - 5} more")
    
    return output_dir, total_size


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Create minimal Data-GR dataset for GitHub')
    parser.add_argument('--source', default='Data-GR', help='Source Data-GR directory')
    parser.add_argument('--output', default='Data-GR-minimal', help='Output directory for minimal dataset')
    parser.add_argument('--max-size', type=float, default=50.0, help='Maximum size in MB (default: 50MB)')
    
    args = parser.parse_args()
    
    source_dir = Path(args.source)
    output_dir = Path(args.output)
    
    if not source_dir.exists():
        print(f"❌ Error: Source directory not found: {source_dir}")
        print("   Please ensure Data-GR folder exists in backend/")
        sys.exit(1)
    
    # Check if output directory exists and ask for confirmation
    if output_dir.exists():
        response = input(f"⚠️  Output directory {output_dir} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Cancelled.")
            sys.exit(0)
        shutil.rmtree(output_dir)
    
    try:
        output_path, total_size = create_minimal_dataset(source_dir, output_dir, args.max_size)
        
        print("\n" + "="*60)
        print("✅ MINIMAL DATASET CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"\n📁 Location: {output_path}")
        print(f"📊 Size: {total_size:.2f} MB")
        print(f"\n💡 Next steps:")
        print(f"   1. Test the minimal dataset:")
        print(f"      cd backend")
        print(f"      python -c \"from trd_data_loader import TRDDataLoader; loader = TRDDataLoader('Data-GR-minimal'); print(f'Found {{len(loader.list_available_tracks())}} tracks')\"")
        print(f"   2. Replace Data-GR with Data-GR-minimal for GitHub")
        print(f"   3. Keep full Data-GR on Kaggle for complete dataset")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

