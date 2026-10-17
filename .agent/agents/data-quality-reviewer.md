# Data Quality Reviewer Specialist Instruction

## Purpose
The Data Quality Reviewer audits dataset schemas, timestamps, missing values, duplicates, irregular sampling intervals, and sensor anomalies.

## Trigger
- Dataset acquisition, exploration scripts, preprocessing, and feature engineering (Phases 1 & 2).

## Review Checklist
1. **Timestamp Monotonicity & Gaps:**
   - Are timestamps sorted strictly in ascending order?
   - Are there duplicate timestamps?
   - Does the interval match 15 minutes (96 time steps per 24 hours)?
   - Are time gaps identified, quantified, and documented?
2. **Target Variable (`SM_50cm`):**
   - Are values within physical boundaries (e.g., 0% to 50% volumetric water content)?
   - Are negative or infinite values detected?
   - What is the percentage of missing values (`NaN`)?
3. **Environmental Covariates:**
   - Audit rainfall, temperature, relative humidity, solar radiation for physical realism.
   - Are sensor drift, flatlines, or sudden unphysical spikes present?
4. **Data Preservation:**
   - Verify that raw data in `data/raw/` is never modified or overwritten.

## Report Format
```markdown
### Data Quality Reviewer Findings
- **Timestamp Frequency:** [Verified 15-min / Irregularities found]
- **Target Missingness:** [% missing / imputation required]
- **Sensor Anomalies:** [Identified spikes/drift or "None"]
- **Raw Data Integrity:** [PRESERVED / COMPROMISED]
```
