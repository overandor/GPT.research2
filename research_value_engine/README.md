# Research Value Engine

A 30-layer appraisal, artifact-generation, and devnet-only synthetic market simulation system for research/IP/code assets.

## Purpose

This system converts research papers, repositories, datasets, and technical notes into diligence-grade artifact packets:

- 30-expert appraisal JSON
- Consensus valuation memo
- Devnet buyer/seller market simulation
- Technical diligence memo
- Grant concept
- Commercialization plan
- Product roadmap
- Buyer listing
- Provenance manifest
- Sale packet ZIP

## Important Warning

This system produces appraisal estimates and synthetic devnet simulations only. It does **not** guarantee market value, buyer demand, grant funding, investment return, patentability, legal ownership, or sale outcome.

## Target Command

```bash
python app.py --asset examples/sample_asset.md --mode full --out 30_outputs
```

## 30-Layer Architecture

1. ingestion
2. provenance
3. secret safety
4. research parser
5. expert panel
6. scoring
7. price engine
8. devnet market
9. negotiation simulation
10. artifact generator
11. grant layer
12. IP layer
13. market mapping
14. productization
15. risk register
16. financial model
17. listing engine
18. packet builder
19. dashboard
20. API
21. database
22. schemas
23. prompts
24. tests
25. examples
26. configs
27. CLI
28. docs
29. deployment
30. outputs

## Current Development Focus

- Convert scaffold into importable Python package
- Add Ollama-backed 30-expert panel
- Add deterministic offline fallback
- Add devnet-only buyer/seller market simulator
- Add marketplace publisher adapters
- Add packet builder and provenance manifest
- Add tests for scoring, pricing, simulation, and safety scanning
