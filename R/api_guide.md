# API Notes

Credit to RAQSAPI library and maintainers. See [direct link](https://github.com/USEPA/RAQSAPI/blob/main/README.md#data-mart-aggregate-functions) for more details.


## Data Mart aggregate functions

These functions retrieve aggregated data from the Data Mart API and are
grouped by how each function aggregates the data. There are 7 different
families of related aggregate functions in which the AQS Data Mart API
groups data.

**These seven families are**:

- **\_by_site**
- **\_by_county**
- **\_by_state**
- **\_by\_\<latitude/longitude bounding box\>** (\_by_box)
- **\_by\_\<monitoring agency\>** (\_by_MA)
- **\_by\_\<Primary Quality Assurance Organization\>** (\_by_pqao)
- **\_by\_\<core based statistical area (as defined by the**  
  **US census Bureau)\>** (\_by_cbsa).

Within these families of aggregated data functions there are functions
that call on the 13 different aggregate services that the Data Mart API
provides. **Note that not all aggregations are available for each
service.**

**These fourteen services are**:

- **Monitors** (aqs_monitors_by\_\*)
- **Sample Data** (aqs_sampledata_by\_\*)
- **Daily Summary Data** (aqs_dailysummary_by\_\*)
- **Annual Summary Data** (aqs_annualsummary_by\_\*)
- **Quarterly Summary Data** (aqs_quarterlysummary_by\_\*)
- **Quality Assurance - Blanks Data** (aqs_qa_blanks_by\_\*)
- **Quality Assurance - Collocated Assessments**
  (aqs_qa_collocated_assessments_by\_\*)
- **Quality Assurance - Flow Rate Verifications**
  (aqs_qa_flowrateverification_by\_\*)
- **Quality Assurance - Flow Rate Audits** (aqs_qa_flowrateaudit_by\_\*)
- **Quality Assurance - One Point Quality Control Raw Data**
  (aqs_qa_one_point_qc_by\_\*)
- **Quality Assurance - PEP Audits** (aqs_qa_pep_audit_by\_\*)
- **Transaction Sample - AQS Submission data in transaction Format
  (RD)** (aqs_transactionsample_by\_\*)
- **Quality Assurance - Annual Performance Evaluations**  
  (aqs_qa_annualperformanceeval_by\_\*)
- **Quality Assurance - Annual Performance Evaluations in the AQS**  
  **Submission transaction format (RD)**
  (aqs_qa_annualperformanceevaltransaction_by\_\*)

Aggregate functions are named AQS_API\<service\>\_\<aggregation\>()
where \<service\> is one of the 13 services listed above and
\<aggregation\> is either “\_by_site”, “\_by_county”, “\_by_state”,
“\_by_box”, “\_by_cbsa”, “\_by_ma”, or “\_by_pqao”.
