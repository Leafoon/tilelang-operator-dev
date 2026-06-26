#!/usr/bin/env python3
"""TileLang Operator Workspace Initialization Script.

Run this script to set up a new operator workspace or validate an existing one.
"""
import argparse
import shutil
import sys
from pathlib import Path


def print_banner():
    print("=" * 60)
    print("  TileLang Operator Workspace Setup")
    print("=" * 60)
    print()


def find_tilelang_source() -> Path | None:
    """Auto-detect TileLang source by checking sibling and parent directories."""
    cwd = Path.cwd().resolve()

    candidates = [
        cwd / "tilelang",           # Same level
        cwd.parent / "tilelang",    # One level up
    ]

    for candidate in candidates:
        init_file = candidate / "tilelang" / "__init__.py"
        if init_file.exists():
            return candidate

    return None


def validate_tilelang_source(path: Path) -> bool:
    """Validate that a path contains a TileLang source checkout."""
    p = path.expanduser().resolve()

    required = [
        p / "tilelang" / "__init__.py",
        p / "tilelang" / "language" / "__init__.py",
    ]

    missing = [r for r in required if not r.is_file()]

    if missing:
        print(f"❌ Missing required TileLang files:")
        for m in missing:
            print(f"   - {m}")
        return False

    optional_dirs = [p / "src" / "transform", p / "src" / "op"]
    has_source = any(d.is_dir() for d in optional_dirs)

    corpus_dirs = [p / "examples", p / "testing", p / "docs"]
    has_corpus = any(d.is_dir() for d in corpus_dirs)

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

    # Auto-detect TileLang source
    tilelang_source = find_tilelang_source()
    if tilelang_source:
        print(f"🔍 Auto-detected TileLang source: {tilelang_source}")
        validate_tilelang_source(tilelang_source)
    else:
        print("ℹ️  TileLang source not auto-detected.")
        print("   The MCP server will search when tools are called.")
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

    # Create new operator
    if args.new_operator:
        print(f"🚀 Creating new operator: {args.new_operator}")
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
