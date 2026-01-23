"""
Security layer for prompt injection detection and bulk extraction prevention
"""
import re
from typing import Tuple, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
from loguru import logger
from backend.core.config import get_settings
from backend.utils.validators import (
    is_valid_query_length,
    contains_sql_injection,
    contains_code_execution_attempts,
    is_enumeration_pattern
)


class SecurityGuard:
    """Security guard for detecting and preventing malicious queries"""
    
    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior|above|earlier)\s+instructions?",
        r"disregard\s+(all\s+)?(previous|prior|above|earlier)",
        r"forget\s+(all\s+)?(previous|prior|above|earlier)",
        r"you\s+are\s+now",
        r"your\s+new\s+(role|instruction|task)\s+is",
        r"system\s+prompt",
        r"show\s+(me\s+)?(your|the)\s+(prompt|instruction|system)",
        r"what\s+(is|are)\s+your\s+(instruction|rule|prompt)",
        r"reveal\s+your\s+(instruction|rule|prompt)",
        r"bypass\s+(security|filter|restriction)",
        r"jailbreak",
        r"DAN\s+mode",
        r"developer\s+mode",
        r"admin\s+mode",
        r"act\s+as\s+if",
        r"pretend\s+(you|to\s+be)",
        r"roleplay\s+as",
    ]
    
    # Sensitive information patterns
    SENSITIVE_PATTERNS = [
        r"api[_\s]?key",
        r"secret[_\s]?key",
        r"password",
        r"token",
        r"credential",
        r"auth[_\s]?token",
    ]
    
    # Data theft patterns (additional protection for sentiment data)
    DATA_THEFT_PATTERNS = [
        r"export\s+(all|entire|complete|full)\s+(data|database|records)",
        r"download\s+(all|entire|complete|full)\s+(data|database)",
        r"give\s+me\s+(all|entire|complete|full|every)\s+(data|records|entries)",
        r"show\s+(all|entire|complete|full|every)\s+(data|records|entries)",
        r"dump\s+(data|database|table|records)",
        r"extract\s+(all|entire|complete)\s+(data|records)",
    ]
    
    def __init__(self):
        self.settings = get_settings()
        self.query_history: Dict[str, list] = defaultdict(list)
        self.blocked_users: Dict[str, datetime] = {}
        
    def _hash_user_id(self, user_id: str) -> str:
        """Hash user ID for privacy"""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    def validate_query(self, query: str, user_id: str = "anonymous") -> Tuple[bool, str, Optional[str]]:
        """
        Validate a query for security issues
        
        Returns:
            (is_valid, reason, warning_message)
        """
        hashed_user = self._hash_user_id(user_id)
        
        # Check if user is blocked
        if hashed_user in self.blocked_users:
            block_time = self.blocked_users[hashed_user]
            if datetime.now() < block_time:
                return False, "User temporarily blocked for suspicious activity", None
            else:
                # Unblock user
                del self.blocked_users[hashed_user]
        
        # Validate query length
        valid, msg = is_valid_query_length(query)
        if not valid:
            return False, msg, None
        
        # Check for prompt injection
        if self._detect_prompt_injection(query):
            logger.warning(f"Prompt injection detected from user {hashed_user}: {query[:100]}")
            self._record_violation(hashed_user, "prompt_injection")
            return False, "Query contains suspicious patterns that may be attempting prompt injection", None
        
        # Check for SQL injection
        if contains_sql_injection(query):
            logger.warning(f"SQL injection detected from user {hashed_user}: {query[:100]}")
            self._record_violation(hashed_user, "sql_injection")
            return False, "Query contains SQL injection patterns", None
        
        # Check for code execution attempts
        if contains_code_execution_attempts(query):
            logger.warning(f"Code execution attempt from user {hashed_user}: {query[:100]}")
            self._record_violation(hashed_user, "code_execution")
            return False, "Query contains code execution patterns", None
        
        # Check for sensitive information requests
        if self._detect_sensitive_info_request(query):
            logger.warning(f"Sensitive info request from user {hashed_user}: {query[:100]}")
            return False, "Query requests sensitive system information", None
        
        # Check for data theft patterns
        if self._detect_data_theft(query):
            logger.warning(f"Data theft attempt from user {hashed_user}: {query[:100]}")
            self._record_violation(hashed_user, "data_theft")
            return False, "This query appears to be attempting to extract proprietary sentiment data. Please ask specific analytical questions instead.", None
        
        # Check for bulk extraction attempts
        is_bulk, warning = self._detect_bulk_extraction(query, hashed_user)
        if is_bulk:
            logger.warning(f"Bulk extraction attempt from user {hashed_user}: {query[:100]}")
            self._record_violation(hashed_user, "bulk_extraction")
            return False, "Query appears to be attempting bulk data extraction. Sephira AI is designed to provide insights and analysis, not raw data exports. Please ask analytical questions.", None
        
        # Check rate limiting
        if not self._check_rate_limit(hashed_user):
            logger.warning(f"Rate limit exceeded for user {hashed_user}")
            return False, "Rate limit exceeded. Please try again later.", None
        
        # Record query
        self._record_query(hashed_user, query)
        
        return True, "OK", warning
    
    def _detect_prompt_injection(self, query: str) -> bool:
        """Detect prompt injection attempts"""
        query_lower = query.lower()
        
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return True
        
        # Additional heuristics
        # Check for unusual delimiter combinations
        delimiters = ['---', '===', '***', '###']
        if any(delim in query for delim in delimiters):
            if any(keyword in query_lower for keyword in ['instruction', 'system', 'prompt', 'ignore']):
                return True
        
        # Check for base64/encoded strings that might hide injection
        if re.search(r"[A-Za-z0-9+/]{50,}={0,2}", query):
            return True
        
        return False
    
    def _detect_sensitive_info_request(self, query: str) -> bool:
        """Detect requests for sensitive information"""
        query_lower = query.lower()
        
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def _detect_data_theft(self, query: str) -> bool:
        """Detect attempts to steal/extract sentiment data"""
        query_lower = query.lower()
        
        for pattern in self.DATA_THEFT_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return True
        
        return False
    
    def _detect_bulk_extraction(self, query: str, user_id: str) -> Tuple[bool, Optional[str]]:
        """Detect bulk data extraction attempts"""
        query_lower = query.lower()
        
        # Check for enumeration patterns
        if is_enumeration_pattern(query):
            return True, None
        
        # Check query history for patterns
        recent_queries = self.query_history[user_id][-10:]  # Last 10 queries
        
        if len(recent_queries) >= 5:
            # Check for similar sequential queries (possible systematic extraction)
            similar_count = 0
            for prev_query, timestamp in recent_queries[-5:]:
                similarity = self._calculate_similarity(query, prev_query)
                if similarity > 0.8:  # Very similar queries
                    similar_count += 1
            
            if similar_count >= 3:
                return True, "Multiple similar queries detected"
        
        # Check for rapid-fire queries
        if len(recent_queries) >= 10:
            recent_times = [ts for _, ts in recent_queries[-10:]]
            time_span = (recent_times[-1] - recent_times[0]).total_seconds()
            if time_span < 30:  # 10 queries in 30 seconds
                return True, "High query frequency detected"
        
        return False, None
    
    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """Calculate similarity between two queries (simple Jaccard similarity)"""
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limits"""
        if not self.settings.rate_limit_enabled:
            return True
        
        recent_queries = self.query_history[user_id]
        now = datetime.now()
        
        # Count queries in last minute
        one_minute_ago = now - timedelta(minutes=1)
        queries_last_minute = sum(
            1 for _, ts in recent_queries if ts > one_minute_ago
        )
        
        if queries_last_minute >= self.settings.max_queries_per_minute:
            return False
        
        # Count queries in last hour
        one_hour_ago = now - timedelta(hours=1)
        queries_last_hour = sum(
            1 for _, ts in recent_queries if ts > one_hour_ago
        )
        
        if queries_last_hour >= self.settings.max_queries_per_hour:
            return False
        
        return True
    
    def _record_query(self, user_id: str, query: str):
        """Record a query in history"""
        self.query_history[user_id].append((query, datetime.now()))
        
        # Keep only last 100 queries per user
        if len(self.query_history[user_id]) > 100:
            self.query_history[user_id] = self.query_history[user_id][-100:]
    
    def _record_violation(self, user_id: str, violation_type: str):
        """Record a security violation"""
        # Count recent violations
        recent_queries = self.query_history[user_id]
        
        # Block user temporarily if too many violations
        violation_count = sum(
            1 for query, _ in recent_queries[-10:]
            if any(pattern in query.lower() for pattern in ['violation', 'blocked'])
        )
        
        if violation_count >= 3:
            # Block for 1 hour
            self.blocked_users[user_id] = datetime.now() + timedelta(hours=1)
            logger.warning(f"User {user_id} blocked for 1 hour due to repeated violations")
    
    def sanitize_response(self, response: str) -> str:
        """Sanitize response to prevent information leakage"""
        # Remove any potential system prompts or instructions
        sensitive_keywords = [
            'system prompt',
            'instruction',
            'you are sephira',
            'your role is',
            'api key',
            'secret'
        ]
        
        response_lower = response.lower()
        for keyword in sensitive_keywords:
            if keyword in response_lower:
                # Log but don't modify - let context decide
                logger.warning(f"Response contains potentially sensitive keyword: {keyword}")
        
        return response
    
    def validate_response_size(self, response: str) -> Tuple[bool, str]:
        """Validate response size to prevent bulk extraction"""
        max_tokens = self.settings.max_response_tokens
        
        # Rough token estimation (1 token ≈ 4 characters)
        estimated_tokens = len(response) / 4
        
        if estimated_tokens > max_tokens:
            return False, f"Response too large (estimated {int(estimated_tokens)} tokens, max {max_tokens})"
        
        return True, "OK"


# Global security guard instance
_security_guard = None


def get_security_guard() -> SecurityGuard:
    """Get global security guard instance"""
    global _security_guard
    if _security_guard is None:
        _security_guard = SecurityGuard()
    return _security_guard
