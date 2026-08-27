from __future__ import annotations

from monarch_api import ReportGroup, ReportResult, ReportSummary

from monarch_mcp.groups import reports


def test_get_report_data_maps_enums_and_filter(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_get_report_data(
        session,
        *,
        filters=None,
        group_by=None,
        timeframe=None,
        sort_by=None,
        fill_empty_values=True,
    ):
        assert session.token == "token-123"
        assert filters.account_ids == ["account-1"]
        assert group_by == [ReportGroup.CATEGORY, ReportGroup.MERCHANT]
        assert timeframe.value == "month"
        assert sort_by.value == "sum"
        assert fill_empty_values is False
        return ReportResult(summary=ReportSummary(total=100.0), rows=[])

    monkeypatch.setattr(reports, "api_get_report_data", fake_get_report_data)

    result = reports.get_report_data(
        filters={"account_ids": ["account-1"]},
        group_by=["category", "merchant"],
        timeframe="month",
        sort_by="sum",
        fill_empty_values=False,
        session_path=str(session_path),
    )

    assert result["summary"]["total"] == 100.0
