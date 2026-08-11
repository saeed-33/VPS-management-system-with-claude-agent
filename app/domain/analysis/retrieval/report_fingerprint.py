import hashlib


class ReportFingerprintService:
    def create(
        self,
        normalized_report: str,
    ) -> str:
        return hashlib.sha256(
            normalized_report.encode(
                "utf-8"
            )
        ).hexdigest()
