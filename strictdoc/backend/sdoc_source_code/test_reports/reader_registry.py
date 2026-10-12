from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc_source_code.test_reports.junit_xml_reader import (
    JUnitXMLReader,
)
from strictdoc.backend.sdoc_source_code.test_reports.robot_xml_reader import (
    RobotOutputXMLReader,
)
from strictdoc.core.file_system.file_tree import File
from strictdoc.core.project_config import ProjectConfig


class TestReportReaderRegistry:
    @staticmethod
    def read_from_file(
        doc_file: File,
        project_config: ProjectConfig,
    ) -> SDocDocument:
        if doc_file.full_path.endswith(".junit.xml"):
            return JUnitXMLReader.read_from_file(doc_file, project_config)
        if doc_file.full_path.endswith(".robot.xml"):
            return RobotOutputXMLReader.read_from_file(doc_file, project_config)
        raise NotImplementedError(doc_file.full_path)
