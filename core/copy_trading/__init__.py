"""
WavexOne Copy Trading Core Automation Package.
Provides 12 reusable components for unified Copy Trading QA architecture:
- AccountManager
- CopyConfigurationManager
- OrderExecutionEngine
- ReplicationValidator
- PositionManager
- MarginMonitor
- StopOutValidator
- CommissionValidator
- WithdrawalValidator
- AccountReconciler
- EvidenceRecorder
- SafeTeardown
"""

from core.copy_trading.session_manager import CopyTradingSessionManager
from core.copy_trading.copy_config_manager import CopyConfigManager
from core.copy_trading.book_poller import BookPoller
from core.copy_trading.evidence_recorder import SanitizedEvidenceRecorder
from core.copy_trading.safe_teardown import SafeTeardownHandler

from core.copy_trading.unified_components import (
    AccountManager,
    CopyConfigurationManager,
    OrderExecutionEngine,
    ReplicationValidator,
    PositionManager,
    MarginMonitor,
    StopOutValidator,
    CommissionValidator,
    ProfitSharingValidator,
    WithdrawalValidator,
    AccountReconciler,
    EvidenceRecorder,
    SafeTeardown
)

__all__ = [
    "CopyTradingSessionManager",
    "CopyConfigManager",
    "BookPoller",
    "SanitizedEvidenceRecorder",
    "SafeTeardownHandler",
    "AccountManager",
    "CopyConfigurationManager",
    "OrderExecutionEngine",
    "ReplicationValidator",
    "PositionManager",
    "MarginMonitor",
    "StopOutValidator",
    "CommissionValidator",
    "ProfitSharingValidator",
    "WithdrawalValidator",
    "AccountReconciler",
    "EvidenceRecorder",
    "SafeTeardown",
]
