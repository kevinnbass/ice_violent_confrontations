#!/usr/bin/env python3
"""
Re-verify specific entries that had errors.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from llm_verify_parallel import ParallelLLMVerifier

async def main():
    base_path = Path(__file__).parent.parent

    # Load API keys
    env_path = Path("C:/Users/kbass/ttuhsc timeline/server/.env")
    api_keys = []

    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('DEEPSEEK_API_KEY'):
                key = line.split('=')[1].strip()
                api_keys.append(key)

    print(f"Loaded {len(api_keys)} API keys")

    # Entries to re-verify (parse/API errors)
    entry_ids = [
        "T2-S-007", "T3-002", "T3-062", "T3-060", "T3-061", "T4-081",
        "T3-139", "T3-121", "T3-133", "T3-184", "T3-197", "T3-P040"
    ]

    # Create verifier
    verifier = ParallelLLMVerifier(
        incidents_dir=base_path / "data" / "incidents",
        sources_dir=base_path / "data" / "sources",
        api_keys=api_keys,
        batch_size=5  # Small batch for re-verification
    )

    # Filter to only the specified entries
    verifier.entries = [e for e in verifier.entries if e["id"] in entry_ids]
    print(f"Found {len(verifier.entries)} entries to re-verify")

    # Run verification
    results, unrelated = await verifier.verify_all()

    # Print summary
    print("\n" + "=" * 60)
    print("RE-VERIFICATION RESULTS")
    print("=" * 60)

    for r in sorted(results, key=lambda x: x.entry_id):
        status = "PASS" if r.passed else "FAIL"
        if r.error:
            status = f"ERROR ({r.error})"
        print(f"{r.entry_id}: {status} (score={r.score})")
        if r.issues:
            print(f"  Issue: {r.issues[0][:80]}")

    # Save results
    output = {
        "results": [
            {
                "entry_id": r.entry_id,
                "score": r.score,
                "passed": r.passed,
                "reasoning": r.reasoning,
                "issues": r.issues,
                "error": r.error
            }
            for r in results
        ],
        "unrelated_sources": [
            {"entry_id": s["entry_id"], "source_name": s["source_name"], "reason": s["reason"]}
            for s in unrelated
        ]
    }

    output_path = base_path / "data" / "sources" / "reverification_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print(f"\nSummary:")
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed and not r.error)
    errors = sum(1 for r in results if r.error)
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Errors: {errors}")

if __name__ == "__main__":
    asyncio.run(main())
