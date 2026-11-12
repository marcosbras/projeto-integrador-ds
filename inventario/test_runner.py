from datetime import datetime
from pathlib import Path
import unittest
from xml.sax.saxutils import escape

from django.conf import settings
from django.test.runner import DiscoverRunner
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class PdfReportingDiscoverRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_result: unittest.TestResult | None = None

    def run_suite(self, suite, **kwargs):
        self.test_result = super().run_suite(suite, **kwargs)
        return self.test_result

    def run_tests(self, test_labels, **kwargs):
        started_at = datetime.now()
        execution_error = None
        try:
            return super().run_tests(test_labels, **kwargs)
        except Exception as exc:
            execution_error = f'{type(exc).__name__}: {exc}'
            raise
        finally:
            report_path = self._write_report(test_labels, started_at, execution_error)
            print(f'\nRelatório de testes salvo em: {report_path}')

    def _write_report(self, test_labels, started_at, execution_error):
        report_directory = Path(settings.BASE_DIR) / 'test-results'
        report_directory.mkdir(parents=True, exist_ok=True)
        report_path = report_directory / (
            f'relatorio-testes-{started_at.strftime("%Y%m%d-%H%M%S-%f")}.pdf'
        )

        result = self.test_result
        failures = result.failures if result else []
        errors = result.errors if result else []
        skipped = result.skipped if result else []
        expected_failures = result.expectedFailures if result else []
        unexpected_successes = result.unexpectedSuccesses if result else []
        tests_run = result.testsRun if result else 0
        passed = max(
            0,
            tests_run
            - len(failures)
            - len(errors)
            - len(skipped)
            - len(expected_failures)
            - len(unexpected_successes),
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Title'],
            alignment=TA_CENTER,
            textColor=colors.HexColor('#16324f'),
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['BodyText'],
            leading=14,
            spaceAfter=5,
        )
        code_style = ParagraphStyle(
            'Traceback',
            parent=styles['Code'],
            fontName='Courier',
            fontSize=7,
            leading=9,
            leftIndent=8,
        )

        story = [
            Paragraph('Relatório de testes locais', title_style),
            Spacer(1, 4 * mm),
            Paragraph(f'Execução iniciada em: {started_at:%d/%m/%Y %H:%M:%S}', body_style),
            Paragraph(f'Escopo: {escape(", ".join(test_labels) or "todos os testes")}', body_style),
        ]

        if execution_error:
            status = 'Execução interrompida com erro'
        elif result and result.wasSuccessful():
            status = 'Sucesso'
        else:
            status = 'Falha'

        summary = [
            ['Resultado', status],
            ['Testes executados', str(tests_run)],
            ['Aprovados', str(passed)],
            ['Falhas', str(len(failures))],
            ['Erros', str(len(errors))],
            ['Ignorados', str(len(skipped))],
            ['Falhas esperadas', str(len(expected_failures))],
            ['Sucessos inesperados', str(len(unexpected_successes))],
        ]
        summary_table = Table(summary, colWidths=[58 * mm, 110 * mm], hAlign='LEFT')
        summary_table.setStyle(
            TableStyle(
                [
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eaf0f6')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#202a35')),
                    ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#c7d1dc')),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 7),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 7),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.extend([Spacer(1, 3 * mm), summary_table, Spacer(1, 6 * mm)])

        anomalies = [
            ('Falhas', failures),
            ('Erros', errors),
            ('Testes ignorados', skipped),
            (
                'Sucessos inesperados',
                [
                    (
                        test,
                        'O teste passou, embora estivesse marcado como falha esperada.',
                    )
                    for test in unexpected_successes
                ],
            ),
        ]
        anomaly_count = sum(len(items) for _, items in anomalies)
        story.append(Paragraph('Anomalias', styles['Heading2']))
        if anomaly_count:
            story.append(Paragraph(f'{anomaly_count} ocorrência(s) registrada(s).', body_style))
            for heading, items in anomalies:
                for test, detail in items:
                    story.append(
                        Paragraph(f'{escape(heading)}: {escape(str(test))}', styles['Heading3'])
                    )
                    if detail:
                        story.append(Preformatted(escape(detail), code_style, maxLineLength=110))
        else:
            story.append(Paragraph('Nenhuma anomalia encontrada.', body_style))

        if expected_failures:
            story.append(Paragraph('Falhas esperadas', styles['Heading2']))
            for test, detail in expected_failures:
                story.append(Paragraph(escape(str(test)), styles['Heading3']))
                if detail:
                    story.append(Preformatted(escape(detail), code_style, maxLineLength=110))

        if execution_error:
            story.extend(
                [
                    Paragraph('Erro durante a execução', styles['Heading2']),
                    Preformatted(escape(execution_error), code_style, maxLineLength=110),
                ]
            )

        document = SimpleDocTemplate(
            str(report_path),
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title='Relatório de testes locais',
            author='Projeto Gestão de Inventário',
        )
        document.build(story)
        return report_path
