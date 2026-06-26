#!/usr/bin/env python3
"""TileLang Operator Workspace Initialization Script.

Run this script to set up a new operator workspace or validate an existing one.
"""
import argparse
import os
import shutil
import sys
from pathlib import Path


def print_banner():
    print("=" * 60)
    print("  TileLang Operator Workspace Setup")
    print("=" * 60)
    print()


def validate_tilelang_source(path: str) -> bool:
    """Validate that a path contains a TileLang source checkout."""
    p = Path(path).expanduser().resolve()

    required = [
        p / "tilelang" / "__init__.py",
        p / "tilelang" / "language" / "__init__.py",
    ]

    optional_dirs = [p / "src" / "transform", p / "src" / "op"]
    has_source = any(d.is_dir() for d in optional_dirs)

    corpus_dirs = [p / "examples", p / "testing", p / "docs"]
    has_corpus = any(d.is_dir() for d in corpus_dirs)

    missing = [r for r in required if not r.is_file()]

    if missing:
        print(f"❌ Missing required TileLang files:")
        for m in missing:
            print(f"   - {m}")
        return False

    if not has_source:
        print(f"⚠️  Missing TileLang source directories (src/transform or src/op)")

    if not has_corpus:
        print(f"⚠️  Missing TileLang corpus directories (examples, testing, or docs)")

    print(f"✅ Valid TileLang source found at: {p}")
    return True


def create_new_operator(name: str, workspace: Path) -> bool:
    """Create a new operator directory from the template."""
    operator_dir = workspace / name
    template_dir = Path(__file__).parent / "example_operator"

    if operator_dir.exists():
        print(f"❌ Operator directory already exists: {operator_dir}")
        return False

    if not template_dir.exists():
        print(f"❌ Template directory not found: {template_dir}")
        return False

    shutil.copytree(template_dir, operator_dir)
    print(f"✅ Created operator: {operator_dir}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Initialize TileLang operator workspace"
    )
    parser.add_argument(
        "--tilelang",
        type=str,
        help="Path to TileLang source checkout",
    )
    parser.add_argument(
        "--new-operator",
        type=str,
        help="Name of a new operator to create from template",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List existing operators in the workspace",
    )

    args = parser.parse_args()
    print_banner()

    workspace = Path.cwd()
    print(f"📂 Working directory: {workspace}")
    print()

    # List existing operators
    if args.list:
        operators = [
            d for d in workspace.iterdir()
            if d.is_dir() and (d / "operator.py").exists()
        ]
        if operators:
            print(f"📦 Operators found ({len(operators)}):")
            for op in operators:
                print(f"   - {op.name}")
        else:
            print("📭 No operators found in current directory")
        return 0

    # Validate TileLang source
    if args.tilelang:
        print("🔍 Validating TileLang source...")
        if not validate_tilelang_source(args.tilelang):
            print(f"\n❌ Please provide a valid TileLang source directory")
            return 1

        # Update .env file
        env_file = workspace / ".env"
        tilelang_path = Path(args.tilelang).expanduser().resolve()

        if env_file.exists():
            content = env_file.read_text()
            if "TILELANG_SOURCE_PATH" in content:
                # Replace existing line
                lines = content.splitlines()
                new_lines = []
                for line in lines:
                    if line.startswith("TILELANG_SOURCE_PATH="):
                        new_lines.append(f"TILELANG_SOURCE_PATH={tilelang_path}")
                    else:
                        new_lines.append(line)
                env_file.write_text("\n".join(new_lines) + "\n")
            else:
                with env_file.open("a") as f:
                    f.write(f"\nTILELANG_SOURCE_PATH={tilelang_path}\n")
        else:
            env_file.write_text(f"# TileLang Operator Development\nTILELANG_SOURCE_PATH={tilelang_path}\n")
        print(f"✅ Updated .env with TILELANG_SOURCE_PATH={tilelang_path}")

    # Create new operator
    if args.new_operator:
        print(f"\n🚀 Creating new operator: {args.new_operator}")
        if not create_new_operator(args.new_operator, workspace):
            return 1
        print(f"\n💡 Next steps:")
        print(f"   1. Edit {args.new_operator}/operator.py")
        print(f"   2. Add tests to {args.new_operator}/test_operator.py")
        print(f"   3. Add benchmarks to {args.new_operator}/benchmark.py")
        print(f"   4. Update {args.new_operator}/README.md")

    print("\n✅ Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
