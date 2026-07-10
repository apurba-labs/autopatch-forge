import os

import requests
import streamlit as st

API_URL = os.getenv(
    "AUTOPATCH_API_URL",
    "http://localhost:8000/api/v1/intercept",
)


def analyze_pipeline(
    repo_url: str,
    branch: str,
    commit_sha: str,
    error_log: str,
) -> dict:
    """
    Sends a pipeline failure to the AutoPatch Forge API
    and returns the remediation response.
    """

    payload = {
        "repo_url": repo_url,
        "branch": branch,
        "commit_sha": commit_sha,
        "error_log": error_log,
    }

    try:

        response = requests.post(
            API_URL,
            json=payload,
            timeout=90,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:

        st.error(
            """
❌ Unable to connect to the AutoPatch Forge API.

Please ensure:

• FastAPI backend is running
• Docker containers are healthy
• API endpoint is reachable
"""
        )

    except requests.exceptions.Timeout:

        st.error(
            "⏱️ The AutoPatch Forge API request timed out."
        )

    except requests.exceptions.HTTPError as e:

        detail = {}

        try:
            detail = e.response.json()
        except Exception:
            detail = {
                "message": e.response.text,
            }

        st.error(
            f"❌ API Error ({e.response.status_code})"
        )

        return {
            "engine_state": "http_error",
            "error": detail,
        }

    except requests.exceptions.RequestException as e:

        st.error(
            f"❌ Request failed: {str(e)}"
        )

    except Exception as e:

        st.exception(e)

    return {
        "incident_id": None,
        "engine_state": "connection_failed",
        "pipeline": [],
        "assessment": {
            "confidence": 0.0,
            "risk": "unknown",
        },
        "metrics": {},
        "telemetry": {},
        "error": "Unable to reach the AutoPatch Forge API.",
    }