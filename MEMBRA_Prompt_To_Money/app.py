import json
from pathlib import Path

ROOT = Path(__file__).parent

PIPELINE = [
    '00_prompt_origin',
    '01_compliance',
    '02_provenance',
    '03_asset_creation',
    '04_measurement',
    '05_benchmarking',
    '06_appraisal',
    '07_prediction',
    '08_panelos',
    '09_productization',
    '10_market',
    '11_liquidity',
    '12_financing',
    '13_payment_settlement',
    '14_delivery',
    '15_profitability',
    '16_audit_feedback',
    '17_scale_loop'
]

DEFAULT_FILES = {
    '00_prompt_origin': ['raw_prompt.txt', 'intent_classification.json', 'safety_scope.md'],
    '01_compliance': ['platform_rules_check.md', 'legal_risk_score.json'],
    '06_appraisal': ['fair_value_report.md', 'floor_price.json'],
    '12_financing': ['loan_prequalification.json', 'advance_rate.json'],
    '15_profitability': ['net_profit_report.md']
}


def ensure_structure():
    for folder in PIPELINE:
        path = ROOT / folder
        path.mkdir(parents=True, exist_ok=True)

        for filename in DEFAULT_FILES.get(folder, []):
            file_path = path / filename
            if not file_path.exists():
                if filename.endswith('.json'):
                    file_path.write_text(json.dumps({'status': 'initialized'}, indent=2))
                else:
                    file_path.write_text(f'# {filename}\n\nInitialized by MEMBRA scaffold.\n')


if __name__ == '__main__':
    ensure_structure()
    print('MEMBRA scaffold initialized.')
