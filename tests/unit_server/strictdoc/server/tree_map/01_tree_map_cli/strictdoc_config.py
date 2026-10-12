from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Test project",
        project_features=[
            "TREE_MAP_SCREEN",
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
        ],
        include_source_paths=[
            "/input/**.py",
            "/input/**.junit.xml",
        ],
    )
    return config
