# AI Prompt History — YottaFlex Churn & Retention Simulator

## AI Tools Used

- **ChatGPT (OpenAI):** Assisted with project planning, code generation, documentation, debugging, validation guidance, and GitHub publishing instructions.
- **VS Code:** Used to inspect and edit project files, execute commands, and review terminal output.
- **Git and GitHub:** Used for version control and publishing the repository.

## Prompt History

The prompts below summarize the AI assistance used during development. They are paraphrases unless replaced with verbatim chat messages.

| Date | Tool | Prompt or request summary | Work performed and verified |
|---|---|---|---|
| 2026-11-05 | ChatGPT | Build an end-to-end churn prediction and retention offer simulator using 20,000 synthetic subscribers, linked tables, a fixed random seed, machine learning, randomized treatment/control, and campaign ROI. | ChatGPT assisted with generating the initial project structure, Python scripts, SQL schema, documentation, tests, and Streamlit dashboard. |
| 2026-11-06 | ChatGPT | Help configure Python and run the project on Windows PowerShell. | Diagnosed Python launcher, virtual environment, script execution policy, and project folder path issues. |
| 2026-11-06 | ChatGPT | Help generate the synthetic customer dataset and run the churn prediction model. | Ran generation for 1,000 customers first, then 20,000 customers. Confirmed 19,493 prediction-cohort customers and 2,802 future churn labels. |
| 2026-11-06 | ChatGPT | Help execute the retention campaign simulation and interpret its metrics. | Verified the dashboard displayed 61.8% treatment retention, 49.8% control retention, and approximately +12.0 percentage points simulated lift. |
| 2026-11-07 | ChatGPT | Help validate the data and run automated tests. | Confirmed 15 validation checks passed and one automated test passed during the initial pipeline test. |
| 2026-11-07 | ChatGPT | Review the README and correct Windows setup and GitHub commands. | Updated the Windows setup instructions and reviewed the project documentation. |
| 2026-11-07 | ChatGPT | Guide me through installing Git, creating a public repository, and pushing the project to GitHub. | Initialized Git, committed project files, pushed the `main` branch, and verified the public GitHub repository. |

## Human Review and Verification

The project was run locally on Windows using Python, PowerShell, and VS Code.

Verified results:

- 20,000 synthetic customer records generated.
- 20,000 subscription records generated.
- 348,185 usage records generated.
- 348,185 billing records generated.
- 22,308 support records generated.
- 19,493 customers included in the prediction cohort.
- 2,802 future churn labels, approximately 14.4%.
- Campaign simulation completed with treatment and control groups.
- Full-dataset validation dashboard reported PASS.
- Four known exception scenarios were registered.
- One automated pipeline test passed during the smaller-scale run.
- Streamlit dashboard opened successfully at `localhost:8501`.
- Source code and documentation were published to a public GitHub repository.

## AI-Use Disclosure

ChatGPT substantially assisted with generating the initial codebase, project structure, documentation, troubleshooting instructions, and development workflow.

The human participant executed the project locally, inspected outputs, checked the dashboard, reviewed validation results, and published the repository.

All customer data is synthetic. Campaign treatment effects and estimated ROI are simulation outputs based on assumptions, not observed real-world causal effects.

## Repository

https://github.com/varshithchinnu02-arch/yottaflex-churn-retention

## Limitations

- The churn model is a prototype and its predictive performance requires further evaluation.
- Simulated retention lift does not establish real-world campaign effectiveness.
- Registered exception scenarios are not proof of automated anomaly detection.
- The generated data is reproducible using the documented seed.
- AI-generated code and documentation require human review before production use.
