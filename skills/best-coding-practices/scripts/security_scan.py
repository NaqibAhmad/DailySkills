#!/usr/bin/env python3
"""
Security scanner for Python/FastAPI codebases.
Detects common vulnerabilities and coding issues.
"""

import ast
import re
import sys
from pathlib import Path
from typing import Iterator, NamedTuple


class Issue(NamedTuple):
    file: Path
    line: int
    severity: str
    category: str
    message: str


class SecurityVisitor(ast.NodeVisitor):
    """AST visitor to detect security issues."""
    
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.issues: list[Issue] = []
    
    def add_issue(self, node: ast.AST, severity: str, category: str, message: str):
        self.issues.append(Issue(
            file=self.file_path,
            line=getattr(node, 'lineno', 0),
            severity=severity,
            category=category,
            message=message
        ))
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # Check for bare except
        if node.type is None:
            self.add_issue(
                node, self.HIGH, "EXCEPTION",
                "Bare 'except:' clause - catches KeyboardInterrupt, SystemExit"
            )
        elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
            self.add_issue(
                node, self.MEDIUM, "EXCEPTION",
                "Overly broad 'except Exception' - catch specific exceptions"
            )
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign):
        # Check for plaintext password assignment
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                if target.attr == "password":
                    # Check if right side is a simple variable (likely from request)
                    if isinstance(node.value, (ast.Name, ast.Attribute)):
                        self.add_issue(
                            node, self.CRITICAL, "SECURITY",
                            f"Potential plaintext password assignment: {target.attr}"
                        )
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        # Check for common SQL injection patterns
        if isinstance(node.func, ast.Attribute):
            # Check for execute with string formatting
            if node.func.attr == "execute":
                if node.args and isinstance(node.args[0], ast.BinOp):
                    if isinstance(node.args[0].op, ast.Mod):
                        self.add_issue(
                            node, self.CRITICAL, "SQL_INJECTION",
                            "String formatting in SQL execute() - use parameterized queries"
                        )
        
        # Check for jwt.decode without verify
        if isinstance(node.func, ast.Attribute) and node.func.attr == "decode":
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "jwt":
                keywords = {kw.arg for kw in node.keywords}
                if "algorithms" not in keywords:
                    self.add_issue(
                        node, self.HIGH, "JWT",
                        "jwt.decode() without 'algorithms' parameter"
                    )
        
        self.generic_visit(node)


def check_file_content(file_path: Path) -> Iterator[Issue]:
    """Check file content with regex patterns."""
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.split('\n')
    
    patterns = [
        (r'print\s*\(', "LOW", "DEBUG", "Debug print statement"),
        (r'\.commit\(\)\s*\n.*for\s+', "MEDIUM", "PERFORMANCE", 
         "Possible commit in loop - consider batching"),
        (r'tokenUrl\s*=\s*["\'][^"\']*["\']', "LOW", "CONFIG",
         "Hardcoded tokenUrl - consider configuration"),
    ]
    
    for line_num, line in enumerate(lines, 1):
        for pattern, severity, category, message in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                yield Issue(file_path, line_num, severity, category, message)


def scan_file(file_path: Path) -> list[Issue]:
    """Scan a single file for issues."""
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
    except SyntaxError as e:
        return [Issue(file_path, e.lineno or 0, "ERROR", "PARSE", str(e))]
    except Exception as e:
        return [Issue(file_path, 0, "ERROR", "READ", str(e))]
    
    visitor = SecurityVisitor(file_path)
    visitor.visit(tree)
    
    # Add regex-based issues
    visitor.issues.extend(check_file_content(file_path))
    
    return visitor.issues


def scan_directory(path: Path, extensions: set[str] = None) -> Iterator[Issue]:
    """Recursively scan directory for issues."""
    if extensions is None:
        extensions = {'.py'}
    
    for file_path in path.rglob('*'):
        if file_path.is_file() and file_path.suffix in extensions:
            yield from scan_file(file_path)


def print_report(issues: list[Issue]):
    """Print formatted issue report."""
    if not issues:
        print("No issues found.")
        return
    
    # Group by severity
    by_severity = {}
    for issue in issues:
        by_severity.setdefault(issue.severity, []).append(issue)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"SECURITY SCAN RESULTS")
    print(f"{'='*60}")
    print(f"Total issues: {len(issues)}")
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "ERROR"]:
        count = len(by_severity.get(severity, []))
        if count:
            print(f"  {severity}: {count}")
    print(f"{'='*60}\n")
    
    # Print details
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "ERROR"]:
        for issue in sorted(by_severity.get(severity, []), key=lambda x: x.file):
            print(f"[{issue.severity}] {issue.file}:{issue.line}")
            print(f"  {issue.category}: {issue.message}\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Scan Python code for security issues"
    )
    parser.add_argument(
        "path",
        nargs='?',
        default='.',
        help="File or directory to scan (default: current directory)"
    )
    parser.add_argument(
        "--fail-on",
        choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        default="HIGH",
        help="Exit with error if issues at this level or higher found"
    )
    
    args = parser.parse_args()
    
    target = Path(args.path)
    if not target.exists():
        print(f"Error: {target} not found")
        sys.exit(1)
    
    if target.is_file():
        issues = scan_file(target)
    else:
        issues = list(scan_directory(target))
    
    print_report(issues)
    
    # Exit with error code if critical/high issues found
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    threshold = severity_order.get(args.fail_on, 1)
    
    for issue in issues:
        if severity_order.get(issue.severity, 99) <= threshold:
            sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
