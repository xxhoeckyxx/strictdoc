from strictdoc.backend.sdoc_source_code.test_reports.robot_xml_reader import (
    normalize_robot_status,
)


def test_normalize_robot_status():
    assert normalize_robot_status("PASS") == "PASSED"
    assert normalize_robot_status("FAIL") == "FAILED"
    assert normalize_robot_status("SKIP") == "SKIP"