# Placement Application Copilot

Which campus roles can I apply for, and what is blocking me? The student workspace checks current role notices and verified profile facts. The placement office workspace reviews ambiguities and updates the same shortlist. The examples are fictional.

The two-workspace design draws on Student360. This project contains independent code, notices and case data.

## Start the demo

**Hosted demo:** [Open Placement Application Copilot](https://placement-copilot-group6.streamlit.app/). The published app was verified in Case simulation mode, including notice precedence and the officer decision. Live Dify requires a published workflow and server-side credentials.

- **Fastest:** Open `demo/Placement_Copilot_Offline_Demo.html` directly in a browser. It shows precomputed synthetic evidence and the officer decision path. It needs no accounts, network, or Python.
- **Interactive project:** Run Streamlit from the project folder with Python 3.11 or later. The default simulation is local and offers the complete case review.
- **Live Dify:** Import the bundled workflow, select an available model, publish a new Dify application and set that application's key as a Streamlit server secret. Follow `workflow/README.md`.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Python 3.12 was used for the release checks. On Windows Command Prompt, activate using `.venv\Scripts\activate`. Read the displayed local URL from the terminal.

### The presentation path

1. Check the three-role shortlist for the sample MBA student.
2. Open **Business Analyst**. Compare the original 12-month requirement with the amended 24-month requirement and the student's verified 18 months.
3. Open **AI Strategy Associate**. Show the governing notice, capstone evidence and absence of an equivalence ruling.
4. In **Placement office**, verify the capstone as equivalent and add a note. Return to the shortlist and show the updated outcome. A reviewer may also request evidence or conclude that the capstone is not equivalent.
5. Open **Evaluation** for the synthetic case comparison.

## Deploy to Streamlit and Dify

The [deployment runbook](docs/deployment.md) lists the repository, branch and entrypoint settings, how to publish the Dify workflow, and how to prove each stage works. Streamlit can serve the complete synthetic simulation without secrets. A verified live agent requires a published Dify app and a provider model configured in that workspace.

## Reproduce the package evidence

```bash
python -m unittest discover -s tests -v
python workflow/verify_workflow.py
python evaluate.py --csv docs/evaluation_offline.csv --review-csv docs/evaluation_review.csv
python demo/build_offline_demo.py
```

On 14 scored synthetic cases, the fixed checklist, optimized rules, and adaptive simulation each reached the expected dispositions, governing notices, deadlines and escalation decisions. The fixed checklist used 46 lookups. Optimized rules and the adaptive simulation both used 43. There were no unsupported ready decisions. All three officer decision cases passed. The local deterministic comparators, workflow-node validation and mocked API checks exercise the synthetic logic. Live Dify model performance and pilot results require separate verification. The officer view simulates staff review within the current app session. Verified rulings remain visible across shortlist rechecks in that session. A demo reset clears them.

## Submission material

- The submission bundle includes `presentation/AgenticAI_Group6_Placement_Copilot.pptx`, the editable deck with presenter notes.
- `docs/pitch-runbook.md` holds the timed pitch, demonstration handoff and Q&A preparation.
- `docs/course-concepts.md` maps the implemented concepts and concepts left outside scope to course pages.
- `docs/architecture.md` describes evidence handling and the application boundary.
- `docs/evaluation_method.md` and `docs/evaluation_offline.csv` describe test conditions and case results.
- `docs/business-evidence.md` records market sources, pricing assumptions and deployment considerations.

Before submission, add full names and roll numbers on slide 1. Enter an owner on each rubric slide, with every student named against at least one attribute. The main pitch leaves room inside the ten-minute time limit. Slides 15 and 16 are Q&A backups.
