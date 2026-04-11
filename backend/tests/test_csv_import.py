from fastapi import status


def test_csv_import_supports_legacy_shapes_and_export(client):
    csv_data = """id,name,year,season,status,type,comment,url,downloaded
1,Frieren,2023,fall,watching,TV,Great show,https://example.com/a,1
Cowboy Bebop,1998,,completed,TV,,,
2,Spirited Away,2001,other,completed,Movie,,https://example.com/b
"""
    response = client.post(
        "/api/v1/import/csv?dry_run=false",
        files={"file": ("anime.csv", csv_data.encode("utf-8"), "text/csv")},
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    body = response.json()
    assert body["summary"]["inserted"] == 3
    assert body["summary"]["duplicates_skipped"] == 0

    list_response = client.get("/api/v1/anime")
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["total"] == 3

    export_response = client.get("/api/v1/export/csv")
    assert export_response.status_code == 200
    assert export_response.headers["content-type"].startswith("text/csv")
    assert "Frieren" in export_response.text
    assert ",other," in export_response.text


def test_csv_import_skips_duplicates(client):
    csv_data = """name,year,season,status,type,comment,url
Frieren,2023,fall,unwatched,TV,,
 frieren ,2023,fall,completed,TV,,
"""
    response = client.post(
        "/api/v1/import/csv",
        files={"file": ("anime.csv", csv_data.encode("utf-8"), "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["inserted"] == 1
    assert body["summary"]["duplicates_skipped"] == 1


def test_csv_import_dry_run_does_not_persist_and_reports_warnings(client):
    csv_data = """name,year,season,status,type,comment,url
Frieren,2023,monsoon,queued,TV,Great show,https://example.com/a
"""
    response = client.post(
        "/api/v1/import/csv?dry_run=true",
        files={"file": ("anime.csv", csv_data.encode("utf-8"), "text/csv")},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["summary"]["dry_run"] is True
    assert body["summary"]["inserted"] == 1
    assert {warning["code"] for warning in body["warnings"]} == {"season_coerced", "status_coerced"}

    list_response = client.get("/api/v1/anime")
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["total"] == 0


def test_csv_import_rejects_empty_file(client):
    response = client.post(
        "/api/v1/import/csv",
        files={"file": ("anime.csv", b"", "text/csv")},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["error"]["code"] == "validation_error"
