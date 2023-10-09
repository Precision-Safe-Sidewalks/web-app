import uuid

import boto3
from django.db import models

from repairs.models.projects import Project


class ProjectSummaryRequest(models.Model):
    """Project summary generation/download request"""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="summary_requests"
    )
    request_id = models.UUIDField(default=uuid.uuid4, editable=False)
    s3_bucket = models.CharField(max_length=255, blank=True, null=True)
    s3_key = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_download_url(self):
        """Return the pre-signed S3 URL"""
        if not (self.s3_bucket and self.s3_key):
            return None

        params = {"Bucket": self.s3_bucket, "Key": self.s3_key}
        expires_in = 10 * 60  # 10 minutes

        s3 = boto3.client("s3")
        return s3.generate_presigned_url(
            "get_object", Params=params, ExpiresIn=expires_in
        )
