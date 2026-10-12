import os
from typing import List

from strictdoc.core.file_system.file_tree import File, FileFinder
from strictdoc.core.project_config import ProjectConfig


class TestReportFilesFinder:
    @staticmethod
    def find_test_report_files(
        project_config: ProjectConfig,
    ) -> List[File]:
        assert project_config.input_paths is not None

        assert isinstance(project_config.output_dir, str)

        report_files: List[File] = []
        for path_to_doc_root_raw in project_config.input_paths:
            if not os.path.exists(path_to_doc_root_raw):
                continue

            path_to_doc_root = path_to_doc_root_raw.rstrip("/")
            path_to_doc_root = os.path.abspath(path_to_doc_root)

            file_tree = FileFinder.find_files_with_extensions(
                root_path=path_to_doc_root,
                ignored_dirs=[project_config.output_dir],
                extensions=[".junit.xml", ".robot.xml"],
                include_paths=project_config.include_source_paths,
                exclude_paths=project_config.exclude_source_paths,
            )

            for _, file, _ in file_tree.iterate():
                report_files.append(file)

        return report_files
