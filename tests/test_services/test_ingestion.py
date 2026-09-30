from io import BytesIO

from app.services.ingestion_service import IngestionService


def test_compute_file_hash_is_deterministic() -> None:
    first = BytesIO(b"a")
    first.name = "a.pdf"
    first.size = 1

    second = BytesIO(b"b")
    second.name = "b.pdf"
    second.size = 1

    hash_one = IngestionService.compute_file_hash([first, second])
    hash_two = IngestionService.compute_file_hash([second, first])

    assert hash_one == hash_two
    assert len(hash_one) == 12
