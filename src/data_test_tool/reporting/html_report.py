from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ..engine.evaluator import EvaluationResult


class HtmlReport:
    @staticmethod
    def write(results: Iterable[EvaluationResult], path: Path) -> None:
        results_list = list(results)
        passed_count = sum(1 for r in results_list if r.passed)
        total_count = len(results_list)
        
        rows = "\n".join(
            f'<tr style="background-color: {'#d4edda' if result.passed else '#f8d7da'};">'
            f'<td>{result.test_name}</td>'
            f'<td><code>{str(result.rule)}</code></td>'
            f'<td style="text-align: center;"><strong>{'✓ PASS' if result.passed else '✗ FAIL'}</strong></td>'
            f'<td>{result.message}</td>'
            f'</tr>'
            for result in results_list
        )
        
        html = f"""
        <html>
        <head>
            <title>Data Testing Platform - Test Report</title>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    border-bottom: 3px solid #007bff;
                    padding-bottom: 10px;
                }}
                .summary {{
                    display: flex;
                    gap: 20px;
                    margin: 20px 0;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                }}
                .summary-item {{
                    flex: 1;
                    text-align: center;
                }}
                .summary-item h3 {{
                    margin: 0;
                    color: #666;
                    font-size: 14px;
                }}
                .summary-item .value {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #007bff;
                    margin: 10px 0 0 0;
                }}
                .summary-item.passed .value {{
                    color: #28a745;
                }}
                .summary-item.failed .value {{
                    color: #dc3545;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                th {{
                    background-color: #007bff;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                }}
                td {{
                    padding: 12px;
                    border-bottom: 1px solid #ddd;
                }}
                tr:hover {{
                    background-color: #f9f9f9;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    text-align: center;
                    color: #888;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>DATA TESTING PLATFORM - TEST REPORT</h1>
                
                <div class="summary">
                    <div class="summary-item passed">
                        <h3>Passed</h3>
                        <div class="value">{passed_count}</div>
                    </div>
                    <div class="summary-item">
                        <h3>Total</h3>
                        <div class="value">{total_count}</div>
                    </div>
                    <div class="summary-item {'failed' if total_count - passed_count > 0 else 'passed'}">
                        <h3>Failed</h3>
                        <div class="value">{total_count - passed_count}</div>
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th width="20%">Test Name</th>
                            <th width="40%">Rule</th>
                            <th width="15%">Status</th>
                            <th width="25%">Message</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
                
                <div class="footer">
                    <p>Generated by Data Testing Platform | {total_count} checks executed</p>
                </div>
            </div>
        </body>
        </html>
        """
        path.write_text(html, encoding='utf-8')
