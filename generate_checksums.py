#!/usr/bin/env python3
"""
Generate SHA256 checksums for all important files
This allows users to verify file integrity
"""
import hashlib
import os
from pathlib import Path

def calculate_sha256(filepath):
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_checksums():
    """Generate checksums for all important files"""
    files_to_check = [
        'youtube_to_mp3.py',
        'requirements.txt',
        'build_exe.py',
        'install_linux.sh',
        'run_linux.sh',
        'setup.bat',
        'run.bat'
    ]

    print("# SHA256 Checksums")
    print("# Generated:", os.popen('date').read().strip())
    print("# Use this to verify file integrity")
    print("# Command: sha256sum <filename>")
    print()

    for filename in files_to_check:
        if os.path.exists(filename):
            checksum = calculate_sha256(filename)
            print(f"{checksum}  {filename}")
        else:
            print(f"# NOT FOUND: {filename}")

    print()
    print("# How to verify:")
    print("# Linux/Mac: sha256sum -c checksums.txt")
    print("# Windows: CertUtil -hashfile <filename> SHA256")

if __name__ == "__main__":
    generate_checksums()

