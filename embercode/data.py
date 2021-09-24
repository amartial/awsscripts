import hashlib
import os

import pytest
import requests

# URL to make requests to
URL = os.environ["URL"]
# JWT token for authentication
AUTH_HEADER = os.environ["AUTH_HEADER"]
# If verifying certs, the path to the FireEye CA_BUNDLE, otherwise false
TLS_VERIFY = os.getenv("TLS_VERIFY", False)  # pylint: disable=W1508


# pylint: disable=W0621
def test_api_1_1(file_to_upload):
    sha256 = __compute_sha256(file_to_upload)
    __1_1_upload(file_to_upload)
    __1_1_get_metadata(sha256)
    __1_1_download(sha256)


# pylint: disable=W0621
def test_api_1_2(file_to_upload):
    sha256 = __compute_sha256(file_to_upload)
    filename = os.path.basename(file_to_upload)
    __1_2_upload(file_to_upload)
    __1_2_get_metadata(sha256)
    __1_2_search(filename)
    __1_2_download(sha256)


@pytest.fixture
def file_to_upload(tmp_path):
    CONTENT = "This smoke test checks that the Central Repo API is working properly."
    p = tmp_path / "smoke_test"
    p.write_text(CONTENT)
    return p


def __compute_sha256(path):
    BLOCKSIZE = 65536
    hasher = hashlib.sha256()
    with open(path, "rb") as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


# pylint: disable=W0621
def __1_1_upload(file_to_upload):
    url = f"{URL}/binaries/1.1/put"

    payload = {
        "tlpColor": "AMBER",
        "classification": "UNDEFINED",
        "contact": "INTEL",
        "source": "GREYMATTER",
    }
    files = [
        (
            "file",
            (
                os.path.basename(file_to_upload),
                open(file_to_upload, "rb"),
                "application/octet-stream",
            ),
        )
    ]
    headers = {
        "Authorization": AUTH_HEADER,
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files, verify=TLS_VERIFY
    )
    assert response.status_code == 200

    body = response.json()
    assert "sha256" in body
    assert "md5" in body
    assert body["msg"] == "SUCCESS"
    assert body["success"] is True


def __1_1_get_metadata(sha256):
    url = f"{URL}/binaries/1.1/get?hash={sha256}"

    payload = {}
    headers = {
        "Authorization": AUTH_HEADER,
    }

    response = requests.request(
        "GET", url, headers=headers, data=payload, verify=TLS_VERIFY
    )
    assert response.status_code == 200

    body = response.json()
    assert "sha256" in body
    assert "url" in body
    assert "md5" in body
    assert "sha1" in body
    assert "classification" in body
    assert "mimeType" in body
    assert "contact" in body
    assert "source" in body
    assert "softDelete" in body
    assert "hardDelete" in body
    assert "tlp" in body
    assert "security" in body
    assert "storage" in body
    assert "submissions" in body
    assert any(
        sub["classification"] == "UNDEFINED"
        and sub["contact"] == "INTEL"
        and sub["source"] == "GREYMATTER"
        and sub["tlpColor"] == "AMBER"
        for sub in body["submissions"]
    )


def __1_1_download(sha256):
    url = f"{URL}/binaries/1.1/get/bytes?hash={sha256}"

    payload = {}
    headers = {
        "Authorization": AUTH_HEADER,
    }

    response = requests.request(
        "GET", url, headers=headers, data=payload, verify=TLS_VERIFY
    )
    assert response.status_code == 200
    assert len(response.content) > 0


def __validate_1_2_metadata(body):
    assert "sha256" in body
    assert "md5" in body
    assert "sha1" in body
    assert "mimeType" in body
    assert "size" in body
    assert "created" in body
    assert "submissions" in body
    assert "tlpColor" in body


def __1_2_upload(path):
    url = f"{URL}/binaries/1.2/file"

    payload = {
        "tlpColor": "AMBER",
        "classification": "UNDEFINED",
        "contact": "INTEL",
        "source": "GREYMATTER",
    }
    files = [
        (
            "file",
            (
                os.path.basename(path),
                open(path, "rb"),
                "application/octet-stream",
            ),
        )
    ]
    headers = {
        "Authorization": AUTH_HEADER,
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files, verify=TLS_VERIFY
    )
    assert response.status_code == 200

    body = response.json()
    __validate_1_2_metadata(body)
    assert any(
        sub["classification"] == "UNDEFINED"
        and sub["contact"] == "INTEL"
        and sub["source"] == "GREYMATTER"
        and sub["tlpColor"] == "AMBER"
        for sub in body["submissions"]
    )


def __1_2_get_metadata(sha256):
    url = f"{URL}/binaries/1.2/file/{sha256}/info"

    payload = {}
    headers = {
        "Authorization": AUTH_HEADER,
    }

    response = requests.request(
        "GET", url, headers=headers, data=payload, verify=TLS_VERIFY
    )
    assert response.status_code == 200

    body = response.json()
    __validate_1_2_metadata(body)
    assert body["tlpColor"] == "AMBER"
    assert any(
        sub["classification"] == "UNDEFINED"
        and sub["contact"] == "INTEL"
        and sub["source"] == "GREYMATTER"
        for sub in body["submissions"]
    )


def __1_2_search(filename):
    url = f"{URL}/binaries/1.2/file/search?filename={filename}"

    payload = {}
    headers = {
        "Authorization": AUTH_HEADER,
    }

    response = requests.request(
        "GET", url, headers=headers, data=payload, verify=TLS_VERIFY
    )
    assert response.status_code == 200

    body = response.json()
    assert len(body) > 0
    for meta in body:
        __validate_1_2_metadata(meta)
    assert any(
        meta["tlpColor"] == "AMBER"
        and any(
            sub["classification"] == "UNDEFINED"
            and sub["contact"] == "INTEL"
            and sub["source"] == "GREYMATTER"
            for sub in meta["submissions"]
        )
        for meta in body
    )


def __1_2_download(sha256):
    url = f"{URL}/binaries/1.2/file/{sha256}"

    payload = {}
    headers = {
        "Authorization": AUTH_HEADER,
    }

    response = requests.request(
        "GET", url, headers=headers, data=payload, verify=TLS_VERIFY
    )
    assert response.status_code == 200
    assert len(response.content) > 0