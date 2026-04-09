"""
@relation(SDOC-SRS-51, scope=file)

PDF print driver abstraction for StrictDoc's HTML2PDF feature.

By default this module uses the external ``html2pdf4doc`` CLI tool.
Optionally, an alternative engine based on Playwright/Chromium can be
enabled by setting the environment variable ``STRICTDOC_HTML2PDF_ENGINE``
to ``"playwright"``.
"""

import os
import os.path
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess, TimeoutExpired, run
from typing import List, Tuple

from html2pdf4doc.main import HPDExitCode

from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html2pdf.pdf_postprocessor import PDFPostprocessor
from strictdoc.helpers.timing import measure_performance


class PDFPrintDriverException(Exception):
    def __init__(self, exception: Exception):
        super().__init__()
        self.exception: Exception = exception

    def get_server_user_message(self) -> str:
        """
        Provide a user-friendly message that describes the underlying exception/error.
        """

        if self.is_could_not_detect_chrome():
            return "HTML2PDF could not detect an existing Chrome installation."

        if self.is_timeout_error():
            return "HTML2PDF timeout error."

        if self.is_js_success_timeout():
            return "HTML2PDF.js success timeout error."

        return "HTML2PDF internal error."

    def is_timeout_error(self) -> bool:
        return isinstance(self.exception, TimeoutExpired)

    def is_could_not_detect_chrome(self) -> bool:
        return (
            isinstance(self.exception, CalledProcessError)
            and self.exception.returncode == HPDExitCode.COULD_NOT_FIND_CHROME
        )

    def is_js_success_timeout(self) -> bool:
        return (
            isinstance(self.exception, CalledProcessError)
            and self.exception.returncode
            == HPDExitCode.DID_NOT_RECEIVE_SUCCESS_STATUS_FROM_HTML2PDF4DOC_JS
        )


class PDFPrintDriver:
    @staticmethod
    def get_pdf_from_html(
        project_config: ProjectConfig,
        paths_to_print: List[Tuple[str, str]],
        path_to_input_root: str,
    ) -> None:
        assert isinstance(paths_to_print, list), paths_to_print

        engine = os.environ.get("STRICTDOC_HTML2PDF_ENGINE", "html2pdf4doc")

        if engine == "playwright":
            PDFPrintDriver._get_pdf_with_playwright(
                project_config, paths_to_print, path_to_input_root
            )
        else:
            # Default: html2pdf4doc CLI.
            PDFPrintDriver._get_pdf_with_html2pdf4doc(
                project_config, paths_to_print, path_to_input_root
            )

    @staticmethod
    def _get_pdf_with_html2pdf4doc(
        project_config: ProjectConfig,
        paths_to_print: List[Tuple[str, str]],
        path_to_input_root: str,
    ) -> None:
        path_to_html2pdf4doc_cache = os.path.join(
            project_config.get_path_to_cache_dir(), "html2pdf"
        )
        cmd: List[str] = [
            # Using sys.executable instead of "python" is important because
            # venv subprocess call to python resolves to wrong interpreter,
            # https://github.com/python/cpython/issues/86207
            # Switching back to calling html2pdf4doc directly because the
            # python -m doesn't work well with PyInstaller.
            # sys.executable, "-m"
            "html2pdf4doc",
            "print",
            "--cache-dir",
            path_to_html2pdf4doc_cache,
        ]
        if project_config.chromedriver is not None:
            cmd.extend(
                [
                    "--chromedriver",
                    project_config.chromedriver,
                ]
            )
        if project_config.html2pdf_strict:
            cmd.append("--strict")
        for path_to_print_ in paths_to_print:
            cmd.append(path_to_print_[0])
            cmd.append(path_to_print_[1])

        with measure_performance(
            "PDFPrintDriver: printing HTML to PDF using HTML2PDF and Chrome Driver"
        ):
            try:
                _: CompletedProcess[bytes] = run(
                    cmd,
                    capture_output=False,
                    check=True,
                )
                PDFPostprocessor.rewrite_cross_document_links(
                    path_to_input_root=path_to_input_root,
                    paths_to_print=paths_to_print,
                )
            except Exception as e_:
                raise PDFPrintDriverException(e_) from e_

    @staticmethod
    def _get_pdf_with_playwright(
        project_config: ProjectConfig,
        paths_to_print: List[Tuple[str, str]],
        path_to_input_root: str,
    ) -> None:
        """Render PDFs using Playwright/Chromium instead of html2pdf4doc.

        Requires the optional ``playwright`` dependency and that a browser
        (e.g. Chromium) has been installed, typically via ``playwright install``.
        """

        try:
            from playwright.sync_api import sync_playwright  # type: ignore[import]
        except ImportError as e_:  # pragma: no cover - optional dependency
            raise PDFPrintDriverException(e_) from e_

        with measure_performance(
            "PDFPrintDriver: printing HTML to PDF using Playwright/Chromium"
        ):
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch()
                    page = browser.new_page()

                    for html_path, pdf_path in paths_to_print:
                        # Ensure output directory exists.
                        Path(pdf_path).parent.mkdir(parents=True, exist_ok=True)

                        # Open the generated HTML via file:// URL so that
                        # relative asset paths resolve correctly.
                        page.goto(Path(html_path).as_uri(), wait_until="networkidle")
                        page.pdf(
                            path=pdf_path,
                            print_background=True,
                        )

                    browser.close()

                PDFPostprocessor.rewrite_cross_document_links(
                    path_to_input_root=path_to_input_root,
                    paths_to_print=paths_to_print,
                )
            except Exception as e_:
                raise PDFPrintDriverException(e_) from e_
