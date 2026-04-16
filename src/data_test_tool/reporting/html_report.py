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
            f'''<tr>
            <td>{result.test_name}</td>
            <td><div class="rule-code">{str(result.rule).replace('<', '&lt;').replace('>', '&gt;')}</div></td>
            <td style="text-align: center;">
                <span class="status-badge {'status-passed' if result.passed else 'status-failed'}">
                    <i class="fas {'fa-check-circle' if result.passed else 'fa-times-circle'}"></i>
                    {'PASS' if result.passed else 'FAIL'}
                </span>
            </td>
            <td>{result.message}</td>
            </tr>'''
            for result in results_list
        )
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Data Testing Platform - Test Report</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: #333;
                    line-height: 1.6;
                }}

                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    padding: 20px;
                }}

                .header {{
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 30px;
                    margin-bottom: 30px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}

                .header h1 {{
                    font-size: 2.5rem;
                    font-weight: 700;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin-bottom: 10px;
                    text-align: center;
                }}

                .header .subtitle {{
                    text-align: center;
                    color: #666;
                    font-size: 1.1rem;
                    margin-bottom: 20px;
                }}

                .timestamp {{
                    text-align: center;
                    color: #888;
                    font-size: 0.9rem;
                }}

                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 25px;
                    margin-bottom: 40px;
                }}

                .stat-card {{
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 30px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }}

                .stat-card::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    background: linear-gradient(90deg, #667eea, #764ba2);
                }}

                .stat-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 30px 60px rgba(0,0,0,0.15);
                }}

                .stat-card.passed {{
                    border-left: 4px solid #10b981;
                }}

                .stat-card.passed::before {{
                    background: linear-gradient(90deg, #10b981, #059669);
                }}

                .stat-card.failed {{
                    border-left: 4px solid #ef4444;
                }}

                .stat-card.failed::before {{
                    background: linear-gradient(90deg, #ef4444, #dc2626);
                }}

                .stat-icon {{
                    font-size: 2.5rem;
                    margin-bottom: 15px;
                    opacity: 0.8;
                }}

                .stat-card.passed .stat-icon {{
                    color: #10b981;
                }}

                .stat-card.failed .stat-icon {{
                    color: #ef4444;
                }}

                .stat-value {{
                    font-size: 3rem;
                    font-weight: 700;
                    margin-bottom: 5px;
                }}

                .stat-card.passed .stat-value {{
                    color: #10b981;
                }}

                .stat-card.failed .stat-value {{
                    color: #ef4444;
                }}

                .stat-label {{
                    font-size: 1.1rem;
                    color: #666;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}

                .progress-section {{
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 30px;
                    margin-bottom: 40px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}

                .progress-bar {{
                    width: 100%;
                    height: 12px;
                    background: #e5e7eb;
                    border-radius: 6px;
                    overflow: hidden;
                    margin: 15px 0;
                }}

                .progress-fill {{
                    height: 100%;
                    background: linear-gradient(90deg, #10b981, #059669);
                    border-radius: 6px;
                    transition: width 0.3s ease;
                }}

                .progress-text {{
                    display: flex;
                    justify-content: space-between;
                    font-size: 0.9rem;
                    color: #666;
                    margin-top: 5px;
                }}

                .results-section {{
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 30px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}

                .section-title {{
                    font-size: 1.8rem;
                    font-weight: 600;
                    margin-bottom: 25px;
                    color: #333;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}

                .section-title i {{
                    color: #667eea;
                }}

                .table-container {{
                    overflow-x: auto;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                }}

                thead {{
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                }}

                th {{
                    padding: 18px 20px;
                    text-align: left;
                    font-weight: 600;
                    font-size: 0.95rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}

                td {{
                    padding: 18px 20px;
                    border-bottom: 1px solid #f3f4f6;
                    font-size: 0.9rem;
                }}

                tbody tr {{
                    transition: all 0.2s ease;
                }}

                tbody tr:hover {{
                    background: #f8fafc;
                    transform: scale(1.01);
                }}

                tbody tr:last-child td {{
                    border-bottom: none;
                }}

                .status-badge {{
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    padding: 6px 12px;
                    border-radius: 20px;
                    font-size: 0.8rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}

                .status-passed {{
                    background: #d1fae5;
                    color: #065f46;
                    border: 1px solid #a7f3d0;
                }}

                .status-failed {{
                    background: #fee2e2;
                    color: #991b1b;
                    border: 1px solid #fecaca;
                }}

                .rule-code {{
                    background: #f3f4f6;
                    padding: 8px 12px;
                    border-radius: 8px;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    font-size: 0.8rem;
                    color: #374151;
                    border: 1px solid #e5e7eb;
                    word-break: break-all;
                }}

                .footer {{
                    text-align: center;
                    padding: 40px 0;
                    color: rgba(255, 255, 255, 0.8);
                    font-size: 0.9rem;
                }}

                .footer a {{
                    color: rgba(255, 255, 255, 0.9);
                    text-decoration: none;
                    font-weight: 500;
                }}

                .footer a:hover {{
                    text-decoration: underline;
                }}

                @media (max-width: 768px) {{
                    .container {{
                        padding: 15px;
                    }}

                    .header {{
                        padding: 20px;
                    }}

                    .header h1 {{
                        font-size: 2rem;
                    }}

                    .stats-grid {{
                        grid-template-columns: 1fr;
                        gap: 15px;
                    }}

                    .stat-card {{
                        padding: 20px;
                    }}

                    .stat-value {{
                        font-size: 2.5rem;
                    }}

                    .results-section {{
                        padding: 20px;
                    }}

                    th, td {{
                        padding: 12px 15px;
                        font-size: 0.85rem;
                    }}
                }}

                @keyframes fadeInUp {{
                    from {{
                        opacity: 0;
                        transform: translateY(30px);
                    }}
                    to {{
                        opacity: 1;
                        transform: translateY(0);
                    }}
                }}

                .stat-card {{
                    animation: fadeInUp 0.6s ease-out;
                }}

                .stat-card:nth-child(1) {{ animation-delay: 0.1s; }}
                .stat-card:nth-child(2) {{ animation-delay: 0.2s; }}
                .stat-card:nth-child(3) {{ animation-delay: 0.3s; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1><i class="fas fa-chart-line"></i> Data Testing Platform</h1>
                    <div class="subtitle">Comprehensive Test Report & Analytics Dashboard</div>
                    <div class="timestamp">Generated on {__import__('datetime').datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
                </div>

                <div class="stats-grid">
                    <div class="stat-card passed">
                        <div class="stat-icon">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <div class="stat-value">{passed_count}</div>
                        <div class="stat-label">Tests Passed</div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-list-check"></i>
                        </div>
                        <div class="stat-value">{total_count}</div>
                        <div class="stat-label">Total Tests</div>
                    </div>

                    <div class="stat-card {'failed' if total_count - passed_count > 0 else 'passed'}">
                        <div class="stat-icon">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <div class="stat-value">{total_count - passed_count}</div>
                        <div class="stat-label">Tests Failed</div>
                    </div>
                </div>

                <div class="progress-section">
                    <div class="section-title">
                        <i class="fas fa-chart-pie"></i>
                        Test Execution Summary
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {passed_count/total_count*100 if total_count > 0 else 0:.1f}%"></div>
                    </div>
                    <div class="progress-text">
                        <span>Success Rate: {passed_count/total_count*100 if total_count > 0 else 0:.1f}%</span>
                        <span>{passed_count} of {total_count} tests passed</span>
                    </div>
                </div>

                <div class="results-section">
                    <div class="section-title">
                        <i class="fas fa-table"></i>
                        Detailed Test Results
                    </div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th><i class="fas fa-tag"></i> Test Name</th>
                                    <th><i class="fas fa-code"></i> Validation Rule</th>
                                    <th><i class="fas fa-info-circle"></i> Status</th>
                                    <th><i class="fas fa-comment"></i> Message</th>
                                </tr>
                            </thead>
                            <tbody>
                                {rows}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="footer">
                    <p>
                        <i class="fas fa-cogs"></i>
                        Generated by <strong>Data Testing Platform</strong> |
                        <a href="https://github.com/robindraec09/data-testing-platform" target="_blank">
                            <i class="fab fa-github"></i> View on GitHub
                        </a> |
                        {total_count} checks executed
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        path.write_text(html, encoding='utf-8')
