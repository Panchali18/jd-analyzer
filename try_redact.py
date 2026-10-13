from presidio_analyzer import AnalyzerEngine

text = """Chukwuemeka Okafor
chuk.okafor@gmail.com | +353 87 123 4567 | 14 Rathmines Road, Dublin 6
Date of birth: 12/03/1991 | Nationality: Nigerian | Married

PROFILE
Business analyst with 6 years' experience at Accenture in Dublin.
He led requirements workshops for a retail client."""

analyzer = AnalyzerEngine()
findings = analyzer.analyze(text=text, language="en")

for item in sorted(findings, key=lambda f: f.start):
    print(f"{item.entity_type:15} {item.score:.2f}  {text[item.start:item.end]}")