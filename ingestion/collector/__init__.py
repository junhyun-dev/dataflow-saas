# Collector Module
from .base import BaseCollector, CollectResult
from .collectors.github_collector import GitHubCollector

__all__ = ["BaseCollector", "CollectResult", "GitHubCollector"]
