#!/usr/bin/env python3
"""
Unified launcher for AutoSHiFt.
This script serves as the main entry point for both CLI and TUI modes.
"""

import os
import sys
from pathlib import Path


def setup_environment():
    """Setup environment variables and paths."""
    # Set up data directory in home
    home = Path(os.environ.get('HOME', '.'))
    data_dir = home / '.autoshift'
    
    # Create data directory if it doesn't exist
    data_dir.mkdir(exist_ok=True)
    
    # Set environment variables for the application
    os.environ.setdefault('SHIFT_DATA_DIR', str(data_dir))
    os.environ.setdefault('SHIFT_COOKIE_FILE', str(data_dir / '.cookies.save'))
    os.environ.setdefault('SHIFT_DB_FILE', str(data_dir / 'keys.db'))
    
    return data_dir


def main():
    """Main entry point."""
    print("AutoSHiFt - Unified Launcher")
    print("============================")
    
    # Setup environment
    data_dir = setup_environment()
    print(f"Using data directory: {data_dir}")
    
    # Determine mode based on arguments
    if len(sys.argv) > 1:
        # CLI mode with arguments
        from autoshift.auto import run
        run()
    else:
        # Default to TUI mode when no arguments provided
        print("Starting TUI interface...")
        try:
            from autoshift.tui import run_tui
            run_tui()
        except ImportError as e:
            print(f"Error starting TUI: {e}")
            print("Falling back to CLI mode...")
            from autoshift.auto import run
            run()


if __name__ == '__main__':
    main()