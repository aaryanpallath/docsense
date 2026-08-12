def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_document_requires_file_or_text(client):
    response = client.post("/documents")
    assert response.status_code == 400


def test_create_list_and_get_document(client):
    create_response = client.post(
        "/documents", data={"text": "Receipt from Acme Corp, total $42.50"}
    )
    assert create_response.status_code == 200
    body = create_response.json()
    assert body["vendor"] == "Test Vendor"
    assert body["total_amount"] == 42.5
    assert body["corrected"] is False
    document_id = body["id"]

    list_response = client.get("/documents")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = client.get(f"/documents/{document_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["id"] == document_id
    assert detail["line_items"][0]["description"] == "Widget"


def test_get_document_not_found(client):
    response = client.get("/documents/9999")
    assert response.status_code == 404


def test_patch_document_updates_fields_and_marks_corrected(client):
    create_response = client.post("/documents", data={"text": "Receipt text"})
    document_id = create_response.json()["id"]

    patch_response = client.patch(
        f"/documents/{document_id}",
        json={"vendor": "Corrected Vendor", "total_amount": 99.99},
    )
    assert patch_response.status_code == 200
    body = patch_response.json()
    assert body["vendor"] == "Corrected Vendor"
    assert body["total_amount"] == 99.99
    assert body["corrected"] is True


def test_patch_document_not_found(client):
    response = client.patch("/documents/9999", json={"vendor": "X"})
    assert response.status_code == 404
