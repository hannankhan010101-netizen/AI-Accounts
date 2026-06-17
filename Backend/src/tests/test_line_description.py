from app.utils.line_description import merge_line_description_fields


class _Line:
    def __init__(self, description=None, description_fields=None):
        self.description = description
        self.description_fields = description_fields


def test_merge_line_description_fields() -> None:
    repo_lines = [{"productCode": "P1", "lineTotal": 100}]
    request_lines = [_Line(description="Widget A", description_fields={"text1": "Batch 1"})]
    out = merge_line_description_fields(repo_lines, request_lines)
    assert out[0]["description"] == "Widget A"
    assert out[0]["descriptionFields"] == {"text1": "Batch 1"}


def test_merge_line_description_fields_skips_blank() -> None:
    repo_lines = [{"productCode": "P1"}]
    request_lines = [_Line(description="  ", description_fields=None)]
    out = merge_line_description_fields(repo_lines, request_lines)
    assert "description" not in out[0]
