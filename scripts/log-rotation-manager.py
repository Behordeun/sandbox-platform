#!/usr/bin/env python3
"""
Log Rotation Manager for DPI Sandbox Platform
Manages log rotation, archival, and cleanup for continuous auditing
"""

import os
import sys
import gzip
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import json


class LogRotationManager:
    """Manages log rotation, compression, and long-term archival"""
    
    def __init__(self, base_log_dir: str = "logs"):
        self.base_log_dir = Path(base_log_dir)
        self.archive_dir = self.base_log_dir / "archive"
        self.compressed_dir = self.archive_dir / "compressed"
        
        # Create directories
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.compressed_dir.mkdir(parents=True, exist_ok=True)
    
    def rotate_logs(self, force: bool = False) -> Dict[str, Any]:
        """Rotate logs based on size and age"""
        results = {
            "rotated_files": [],
            "compressed_files": [],
            "archived_files": [],
            "errors": []
        }
        
        # Find all log directories
        log_dirs = [
            self.base_log_dir / "services" / "logs",
            self.base_log_dir / "sandbox" / "logs",
            Path("services/logs"),
            Path("sandbox/logs")
        ]
        
        for log_dir in log_dirs:
            if log_dir.exists():
                results.update(self._process_log_directory(log_dir, force))
        
        return results
    
    def _process_log_directory(self, log_dir: Path, force: bool) -> Dict[str, Any]:
        """Process a single log directory"""
        results = {
            "rotated_files": [],
            "compressed_files": [],
            "archived_files": [],
            "errors": []
        }
        
        try:
            # Find log files
            log_files = list(log_dir.glob("*.log"))
            
            for log_file in log_files:
                try:
                    # Check if rotation is needed
                    if self._should_rotate(log_file, force):
                        rotated_file = self._rotate_single_file(log_file)
                        results["rotated_files"].append(str(rotated_file))
                        
                        # Compress the rotated file
                        compressed_file = self._compress_file(rotated_file)
                        if compressed_file:
                            results["compressed_files"].append(str(compressed_file))
                    
                    # Archive old rotated files
                    archived = self._archive_old_files(log_file)
                    results["archived_files"].extend(archived)
                    
                except Exception as e:
                    results["errors"].append(f"Error processing {log_file}: {str(e)}")
        
        except Exception as e:
            results["errors"].append(f"Error processing directory {log_dir}: {str(e)}")
        
        return results
    
    def _should_rotate(self, log_file: Path, force: bool) -> bool:
        """Check if a log file should be rotated"""
        if force:
            return True
        
        if not log_file.exists():
            return False
        
        # Check file size (rotate if > 50MB)
        size_mb = log_file.stat().st_size / (1024 * 1024)
        if size_mb > 50:
            return True
        
        # Check file age (rotate if > 7 days)
        age_days = (datetime.now().timestamp() - log_file.stat().st_mtime) / (24 * 3600)
        if age_days > 7:
            return True
        
        return False
    
    def _rotate_single_file(self, log_file: Path) -> Path:
        """Rotate a single log file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated_name = f"{log_file.stem}_{timestamp}.log"
        rotated_path = log_file.parent / rotated_name
        
        # Move current log to rotated name
        shutil.move(str(log_file), str(rotated_path))
        
        # Create new empty log file
        log_file.touch()
        
        return rotated_path
    
    def _compress_file(self, file_path: Path) -> Path:
        """Compress a log file using gzip"""
        compressed_path = self.compressed_dir / f"{file_path.name}.gz"
        
        try:
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove original file after compression
            file_path.unlink()
            
            return compressed_path
        
        except Exception as e:
            print(f"Error compressing {file_path}: {e}")
            return None
    
    def _archive_old_files(self, base_log_file: Path) -> List[str]:
        """Archive old rotated files"""
        archived = []
        
        # Find old rotated files (older than 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        
        pattern = f"{base_log_file.stem}_*.log*"
        old_files = list(base_log_file.parent.glob(pattern))
        
        for old_file in old_files:
            try:
                file_date = datetime.fromtimestamp(old_file.stat().st_mtime)
                if file_date < cutoff_date:
                    # Move to archive directory
                    archive_path = self.archive_dir / old_file.name
                    shutil.move(str(old_file), str(archive_path))
                    archived.append(str(archive_path))
            
            except Exception as e:
                print(f"Error archiving {old_file}: {e}")
        
        return archived
    
    def cleanup_old_archives(self, days_to_keep: int = 365) -> Dict[str, Any]:
        """Clean up very old archived files"""
        results = {
            "deleted_files": [],
            "errors": [],
            "space_freed_mb": 0
        }
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Clean compressed archives
        for archive_file in self.compressed_dir.rglob("*"):
            if archive_file.is_file():
                try:
                    file_date = datetime.fromtimestamp(archive_file.stat().st_mtime)
                    if file_date < cutoff_date:
                        size_mb = archive_file.stat().st_size / (1024 * 1024)
                        archive_file.unlink()
                        results["deleted_files"].append(str(archive_file))
                        results["space_freed_mb"] += size_mb
                
                except Exception as e:
                    results["errors"].append(f"Error deleting {archive_file}: {str(e)}")
        
        return results
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get comprehensive log statistics"""
        stats = {
            "active_logs": {},
            "archived_logs": {},
            "compressed_logs": {},
            "total_size_mb": 0,
            "oldest_log": None,
            "newest_log": None
        }
        
        # Scan all log directories
        all_dirs = [
            Path("services/logs"),
            Path("sandbox/logs"),
            self.archive_dir,
            self.compressed_dir
        ]
        
        all_files = []
        for log_dir in all_dirs:
            if log_dir.exists():
                all_files.extend(log_dir.rglob("*.log*"))
        
        for log_file in all_files:
            if log_file.is_file():
                try:
                    stat = log_file.stat()
                    size_mb = stat.st_size / (1024 * 1024)
                    mod_time = datetime.fromtimestamp(stat.st_mtime)
                    
                    # Categorize file
                    if "compressed" in str(log_file):
                        category = "compressed_logs"
                    elif "archive" in str(log_file):
                        category = "archived_logs"
                    else:
                        category = "active_logs"
                    
                    stats[category][str(log_file)] = {
                        "size_mb": round(size_mb, 2),
                        "last_modified": mod_time.isoformat(),
                        "age_days": (datetime.now() - mod_time).days
                    }
                    
                    stats["total_size_mb"] += size_mb
                    
                    # Track oldest and newest
                    if not stats["oldest_log"] or mod_time < datetime.fromisoformat(stats["oldest_log"]["date"]):
                        stats["oldest_log"] = {"file": str(log_file), "date": mod_time.isoformat()}
                    
                    if not stats["newest_log"] or mod_time > datetime.fromisoformat(stats["newest_log"]["date"]):
                        stats["newest_log"] = {"file": str(log_file), "date": mod_time.isoformat()}
                
                except Exception as e:
                    print(f"Error processing {log_file}: {e}")
        
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        return stats


def main():
    parser = argparse.ArgumentParser(description="DPI Sandbox Log Rotation Manager")
    parser.add_argument("--rotate", action="store_true", help="Rotate logs")
    parser.add_argument("--force", action="store_true", help="Force rotation regardless of size/age")
    parser.add_argument("--cleanup", type=int, metavar="DAYS", help="Clean up archives older than DAYS")
    parser.add_argument("--stats", action="store_true", help="Show log statistics")
    parser.add_argument("--log-dir", default="logs", help="Base log directory")
    
    args = parser.parse_args()
    
    manager = LogRotationManager(args.log_dir)
    
    if args.rotate:
        print("🔄 Rotating logs...")
        results = manager.rotate_logs(args.force)
        print(f"✅ Rotated {len(results['rotated_files'])} files")
        print(f"📦 Compressed {len(results['compressed_files'])} files")
        print(f"📁 Archived {len(results['archived_files'])} files")
        if results['errors']:
            print(f"❌ {len(results['errors'])} errors occurred")
            for error in results['errors']:
                print(f"   {error}")
    
    if args.cleanup:
        print(f"🧹 Cleaning up archives older than {args.cleanup} days...")
        results = manager.cleanup_old_archives(args.cleanup)
        print(f"🗑️  Deleted {len(results['deleted_files'])} files")
        print(f"💾 Freed {results['space_freed_mb']:.2f} MB")
        if results['errors']:
            print(f"❌ {len(results['errors'])} errors occurred")
    
    if args.stats:
        print("📊 Log Statistics:")
        stats = manager.get_log_statistics()
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()