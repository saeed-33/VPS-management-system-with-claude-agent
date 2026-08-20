"""Class extracted from specialist_execution_service during the structure refactor."""

from __future__ import annotations

import logging

from dataclasses import replace

from uuid import uuid4

from app.capabilities.investigation.correlation.cross_specialist_correlator import CrossSpecialistCorrelator

from app.capabilities.investigation.execution_contracts.investigation_execution_result import InvestigationExecutionResult
from app.capabilities.investigation.execution_contracts.investigation_specialist_run import InvestigationSpecialistRun

from app.capabilities.investigation.final_diagnosis_synthesizer.final_diagnosis_synthesizer import FinalDiagnosisSynthesizer

from app.capabilities.investigation.runtime_snapshot_service.runtime_snapshot_service import InvestigationRuntimeSnapshotService

from app.capabilities.investigation.specialist_investigation_loop.specialist_investigation_loop_result import SpecialistInvestigationLoopResult
from app.capabilities.investigation.specialist_investigation_loop.specialist_loop_stop_reason import SpecialistLoopStopReason

from app.core.contracts.investigation.evidence_kind import EvidenceKind
from app.core.contracts.investigation.evidence_reference import EvidenceReference
from app.core.contracts.investigation.investigation_budget import InvestigationBudget
from app.core.contracts.investigation.investigation_finding import InvestigationFinding
from app.core.contracts.investigation.investigation_hypothesis import InvestigationHypothesis
from app.core.contracts.investigation.investigation_status import InvestigationStatus
from app.core.contracts.investigation.server_investigation_state import ServerInvestigationState
from app.core.contracts.investigation.specialist_result import SpecialistResult
from app.core.contracts.investigation.specialist_task import SpecialistTask
from app.core.contracts.investigation.specialist_task_status import SpecialistTaskStatus

class SpecialistExecutionInProgress(RuntimeError):
    """
    يمثل حجز تنفيذ اختصاصي لم يكتمل بعد.
    """
    pass
