#!/usr/bin/env python
"""
Generate ICE Violence Maps
==========================
Command-line script to generate all types of choropleth maps.

Usage:
    python generate_maps.py           # Generate all maps
    python generate_maps.py --basic   # Basic violence ratio maps only
    python generate_maps.py --tiered  # Tiered maps only
    python generate_maps.py --category # Category maps only
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import OUTPUT_DIR


def main():
    """Generate ICE violence maps."""
    parser = argparse.ArgumentParser(description='Generate ICE Violence Maps')
    parser.add_argument('--basic', action='store_true', help='Generate basic violence ratio maps only')
    parser.add_argument('--tiered', action='store_true', help='Generate tiered maps only')
    parser.add_argument('--category', action='store_true', help='Generate category maps only')
    parser.add_argument('--output-dir', type=str, default=None, help='Output directory for maps')

    args = parser.parse_args()

    # If no specific option, generate all
    generate_all = not (args.basic or args.tiered or args.category)

    # Set output directory
    output_dir = Path(args.output_dir) if args.output_dir else OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("ICE Violence Map Generator")
    print("=" * 60)
    print(f"Output directory: {output_dir}")
    print()

    try:
        from ice_arrests.visualization import (
            create_violence_ratio_map,
            create_dual_panel_map,
            create_tiered_ratio_maps,
            create_isolated_tier_ratio_maps,
            generate_all_category_maps,
        )

        # Basic maps
        if generate_all or args.basic:
            print("\n--- BASIC VIOLENCE RATIO MAPS ---")

            print("\nGenerating single-panel violence ratio map...")
            create_violence_ratio_map(output_path=output_dir / 'ice_violence_ratio_map.png')

            print("Generating dual-panel map...")
            create_dual_panel_map(output_path=output_dir / 'ice_violence_dual_panel_map.png')

        # Tiered maps
        if generate_all or args.tiered:
            print("\n--- TIERED MAPS ---")

            print("\nGenerating cumulative tiered ratio maps...")
            create_tiered_ratio_maps(output_path=output_dir / 'ice_ratio_by_tier_ALL.png')

            print("Generating isolated tier ratio maps...")
            create_isolated_tier_ratio_maps(output_path=output_dir / 'ice_ratio_ISOLATED_ALL.png')

        # Category maps
        if generate_all or args.category:
            print("\n--- CATEGORY MAPS ---")
            generate_all_category_maps(output_dir=output_dir)

        print("\n" + "=" * 60)
        print("COMPLETE!")
        print("=" * 60)
        print(f"\nMaps saved to: {output_dir}")

        # List generated files
        map_files = list(output_dir.glob('ice_*.png'))
        if map_files:
            print(f"\nGenerated {len(map_files)} map files:")
            for f in sorted(map_files):
                print(f"  - {f.name}")

    except ImportError as e:
        print(f"Error: Could not import required modules: {e}")
        print("\nFalling back to legacy scripts...")

        # Fall back to legacy scripts
        if generate_all or args.basic:
            try:
                from generate_violence_map import create_violence_ratio_map, create_dual_panel_map
                create_violence_ratio_map(output_path=output_dir / 'ice_violence_ratio_map.png')
                create_dual_panel_map(output_path=output_dir / 'ice_violence_dual_panel_map.png')
            except ImportError as e2:
                print(f"  Legacy generate_violence_map failed: {e2}")

        if generate_all or args.tiered:
            try:
                from generate_tiered_maps import create_tiered_ratio_maps, create_isolated_tier_ratio_maps
                create_tiered_ratio_maps(output_path=output_dir / 'ice_ratio_by_tier_ALL.png')
                create_isolated_tier_ratio_maps(output_path=output_dir / 'ice_ratio_ISOLATED_ALL.png')
            except ImportError as e2:
                print(f"  Legacy generate_tiered_maps failed: {e2}")

        print("\nNote: Some maps may not have been generated due to import errors.")
        print("Please ensure the ice_arrests package is properly installed.")

    except Exception as e:
        print(f"\nError generating maps: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
