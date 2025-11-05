import pytest

from src.autoscription.core.errors import MappingIdikaResponseException
from src.autoscription.idika_client.mapping.clinical_document_mt import map_author
from src.autoscription.idika_client.model.idika.clinical_document import (
    AssignedAuthor,
    Author,
    Id,
)
from src.autoscription.idika_client.model.mt.clinical_document.author import (
    Author as AuthorMt,
)


class TestMappingAuthor:
    def test_map_author_happy_path(self):
        author = Author(
            assigned_author=AssignedAuthor(
                id=[Id(root="1.19.1", extension="specialty_id"), Id(root="1.19.2", extension="specialty_name")]
            )
        )
        result = map_author(author)
        assert isinstance(result, AuthorMt)
        assert result.assigned_author.doctor_specialty_id == "specialty_id"
        assert result.assigned_author.doctor_specialty_name == "specialty_name"

    def test_map_author_missing_assigned_author(self):
        author = Author()
        with pytest.raises(MappingIdikaResponseException):
            map_author(author)

    def test_map_author_missing_required_ids(self):
        author = Author(assigned_author=AssignedAuthor(id=[Id(root="1.19.1", extension="specialty_id")]))
        with pytest.raises(MappingIdikaResponseException):
            map_author(author)
