#!/usr/bin/env python
"""
Run ICE Enforcement Analysis
============================
Command-line script to run analysis and generate reports.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import OUTPUT_DIR


def run_merged_analysis():
    """Run the merged dataset analysis."""
    print("\n" + "=" * 80)
    print("FINAL MERGED ANALYSIS")
    print("=" * 80)

    try:
        from ice_arrests.analysis.merge import create_merged_dataset, aggregate_by_classification

        df = create_merged_dataset()

        # Print summary
        print(f"\nStates in dataset: {len(df)}")
        print(f"Total arrests: {df['arrests'].sum():,}")
        print(f"Total incidents: {df['total_violent_incidents'].sum()}")

        # Aggregate by classification
        agg_df = aggregate_by_classification(df)
        print("\nBy Classification:")
        print(agg_df.to_string(index=False))

        # Save to CSV
        output_path = OUTPUT_DIR / 'FINAL_MERGED_DATASET.csv'
        df.to_csv(output_path, index=False)
        print(f"\nSaved: {output_path}")

        return df

    except ImportError as e:
        print(f"Error: {e}")
        print("Falling back to legacy FINAL_MERGED_DATABASE.py...")
        from FINAL_MERGED_DATABASE import print_analysis
        return print_analysis()


def run_tiered_analysis():
    """Run the tiered confidence analysis."""
    print("\n" + "=" * 80)
    print("TIERED CONFIDENCE ANALYSIS")
    print("=" * 80)

    try:
        from ice_arrests.analysis.tiered import (
            calculate_confidence_adjusted_ratios,
            analyze_by_classification_with_confidence,
            get_tier_summary,
        )

        # Get tier summary
        summary = get_tier_summary()
        print("\nIncidents by Tier:")
        for tier, data in summary.items():
            print(f"  Tier {tier}: {data['total']} incidents ({data['deaths']} deaths)")

        # Get confidence-adjusted ratios
        df = calculate_confidence_adjusted_ratios()
        print(f"\nStates analyzed: {len(df)}")
        print(f"States with incidents: {len(df[df['total_high_confidence_incidents'] > 0])}")

        # Save
        output_path = OUTPUT_DIR / 'STATE_ANALYSIS_WITH_CONFIDENCE.csv'
        df.to_csv(output_path, index=False)
        print(f"\nSaved: {output_path}")

        return df

    except ImportError as e:
        print(f"Error: {e}")
        print("Falling back to legacy TIERED_ANALYSIS.py...")
        from TIERED_ANALYSIS import print_tiered_analysis
        return print_tiered_analysis()


def main():
    """Run all analyses."""
    print("=" * 80)
    print("ICE ENFORCEMENT ANALYSIS")
    print("=" * 80)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Run analyses
    merged_df = run_merged_analysis()
    tiered_df = run_tiered_analysis()

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nOutput files saved to: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
