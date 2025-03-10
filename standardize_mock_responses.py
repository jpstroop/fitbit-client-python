#!/usr/bin/env python3
"""
Script to standardize mock_response usage in test files.

This script finds test files that use direct mock_response manipulation and
converts them to use mock_response_factory instead.
"""

# Standard library imports
import os
from pathlib import Path
import re
import sys
from typing import List
from typing import Tuple


def find_pattern_in_file(file_path: str, pattern: str) -> List[str]:
    """Find all matches of pattern in the given file."""
    with open(file_path, "r") as f:
        content = f.read()
    return re.findall(pattern, content, re.MULTILINE)


def transform_file(file_path: str, dry_run: bool = False) -> bool:
    """Transform a file to use mock_response_factory."""
    with open(file_path, "r") as f:
        content = f.read()

    # Backup original content
    original_content = content

    # Pattern 1: def test_*(mock_response) -> def test_*(mock_response_factory)
    # Find all test function definitions
    test_pattern = r"(def\s+test_\w+\([^)]*)(,\s*mock_response)(\s*[,)].*)"

    def param_replacement(match):
        before = match.group(1)
        param = match.group(2).replace("mock_response", "mock_response_factory")
        after = match.group(3)
        return f"{before}{param}{after}"

    content = re.sub(test_pattern, param_replacement, content)

    # Pattern 2: mock_response.json.return_value = {...}
    pattern2 = r"([ \t]*)mock_response\.json\.return_value\s*=\s*({[^;]*}|\[[^;]*\])"

    def replacement2(match):
        indent = match.group(1)
        data = match.group(2).strip()
        # Ensure data has balanced braces
        open_braces = data.count("{") - data.count("}")
        open_brackets = data.count("[") - data.count("]")

        if open_braces != 0 or open_brackets != 0:
            # Skip this match as it has unbalanced braces or brackets
            return match.group(0)

        return f"{indent}mock_response = mock_response_factory(\n{indent}    200, \n{indent}    {data}\n{indent})"

    content = re.sub(pattern2, replacement2, content)

    # Pattern 3: mock_response.status_code = 204
    pattern3 = r"([ \t]*)mock_response\.status_code\s*=\s*(\d+)"

    def replacement3(match):
        indent = match.group(1)
        status_code = match.group(2)
        return f"{indent}mock_response = mock_response_factory({status_code})"

    content = re.sub(pattern3, replacement3, content)

    # Pattern 4: We're disabling this pattern for now as it was causing issues
    # The goal was to change order of assignments (response assignment should come before oauth assignment)
    # but it was causing syntax errors
    """
    pattern4 = r'([ \t]*)(.*?)\.oauth(?:\.|\w+\.)*request\.return_value\s*=\s*mock_response\n([ \t]*)mock_response\s*=\s*mock_response_factory'
    
    def replacement4(match):
        indent1 = match.group(1)
        obj = match.group(2)
        indent2 = match.group(3)
        return f"{indent2}mock_response = mock_response_factory\n{indent1}{obj}.oauth.request.return_value = mock_response"
    
    content = re.sub(pattern4, replacement4, content)
    """

    # Pattern 5: Fix cases where test was updated to use mock_response_factory as parameter
    # but still uses mock_response in the body
    pattern5 = r"def\s+test_\w+\([^)]*mock_response_factory[^)]*\).*?(?=\n\s*def|\Z)"

    def fix_mock_response_usage(match):
        test_func = match.group(0)
        # If the function uses mock_response_factory but also has direct mock_response usage
        if (
            "mock_response.json.return_value =" in test_func
            or "mock_response.status_code =" in test_func
        ):
            # Add a mock_response declaration at the beginning of the function body
            # Find the first indented line after the function def
            lines = test_func.split("\n")
            for i, line in enumerate(lines):
                if i > 0 and line.strip() and not line.strip().startswith("#"):
                    indent = re.match(r"(\s*)", line).group(1)
                    # Insert the mock_response assignment after docstring (if any)
                    for j in range(i, len(lines)):
                        if not lines[j].strip().startswith('"""') and not lines[
                            j
                        ].strip().startswith("'''"):
                            lines.insert(j, f"{indent}mock_response = mock_response_factory(200)")
                            break
                    break
            return "\n".join(lines)
        return test_func

    content = re.sub(pattern5, fix_mock_response_usage, content, flags=re.DOTALL)

    # If no changes were made, return False
    if content == original_content:
        return False

    # Write the changes back to the file
    if not dry_run:
        with open(file_path, "w") as f:
            f.write(content)

    return True


def find_files_to_transform() -> List[Tuple[str, bool]]:
    """Find all test files that need to be transformed."""
    test_dir = Path("tests")
    result = []

    for root, _, files in os.walk(test_dir):
        for file in files:
            if file.endswith(".py") and file.startswith("test_"):
                file_path = os.path.join(root, file)

                # Check if file uses mock_response directly
                uses_mock_response = bool(
                    find_pattern_in_file(
                        file_path, r"def\s+test_\w+\([^)]*,\s*mock_response\s*[,)]"
                    )
                )

                # Check if file directly manipulates mock_response
                manipulates_mock_response = bool(
                    find_pattern_in_file(
                        file_path, r"mock_response\.(json\.return_value|status_code)\s*="
                    )
                )

                # Check if file uses mock_response_factory
                uses_factory = bool(
                    find_pattern_in_file(file_path, r"mock_response\s*=\s*mock_response_factory")
                )

                # Determine if file needs transformation
                needs_transform = (
                    uses_mock_response or manipulates_mock_response
                ) and not uses_factory

                if needs_transform:
                    result.append((file_path, needs_transform))

    return result


def main():
    """Main entry point."""
    dry_run = "--dry-run" in sys.argv
    files = find_files_to_transform()

    print(f"Found {len(files)} files that need to be transformed.")
    if dry_run:
        print("Running in dry-run mode. No files will be modified.")

    for file_path, _ in files:
        print(f"Transforming {file_path}...", end="")
        transformed = transform_file(file_path, dry_run)
        print(" TRANSFORMED" if transformed else " SKIPPED (no changes)")

    print("\nDone!")
    print(f"Transformed {len(files)} files.")

    if dry_run:
        print("\nRun without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
