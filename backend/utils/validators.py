"""
Input validation utilities
"""
import re
from typing import Tuple


def is_valid_query_length(query: str, min_length: int = 1, max_length: int = 1000) -> Tuple[bool, str]:
    """Validate query length"""
    if len(query) < min_length:
        return False, f"Query too short (minimum {min_length} characters)"
    if len(query) > max_length:
        return False, f"Query too long (maximum {max_length} characters)"
    return True, "OK"


def contains_sql_injection(query: str) -> bool:
    """Check for SQL injection patterns"""
    sql_patterns = [
        r"(union\s+select|drop\s+table|delete\s+from|insert\s+into|update\s+set)",
        r"(--|;|\/\*|\*\/|xp_|sp_)",
        r"(\bor\b\s+\d+\s*=\s*\d+|\band\b\s+\d+\s*=\s*\d+)"
    ]
    
    query_lower = query.lower()
    for pattern in sql_patterns:
        if re.search(pattern, query_lower):
            return True
    return False


def contains_code_execution_attempts(query: str) -> bool:
    """Check for code execution attempts"""
    code_patterns = [
        r"(eval|exec|compile|__import__|subprocess|os\.system)",
        r"(exec\(|eval\(|__builtins__|globals\(|locals\()",
        r"(pickle|marshal|importlib)"
    ]
    
    query_lower = query.lower()
    for pattern in code_patterns:
        if re.search(pattern, query_lower):
            return True
    return False


def is_enumeration_pattern(query: str) -> bool:
    """Detect systematic enumeration patterns"""
    enumeration_patterns = [
        r"(give\s+me\s+all|list\s+all|show\s+all|dump\s+all)",
        r"(every\s+record|every\s+entry|all\s+records|all\s+entries)",
        r"(from\s+\d+\s+to\s+\d+|between\s+\d+\s+and\s+\d+)"
    ]
    
    query_lower = query.lower()
    for pattern in enumeration_patterns:
        if re.search(pattern, query_lower):
            return True
    return False
