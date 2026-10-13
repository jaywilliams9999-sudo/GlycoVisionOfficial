# GlycoVisionOfficial
GlycoVision is an explainable Type 2 diabetes risk assessment web application built for clinicians. It calculates a risk score and color-coded risk level based on patient biomarkers, utilizing SHAP (SHapley Additive exPlanations) to provide a transparent breakdown of exactly how each biomarker influenced the prediction.

#This is for developers
1. Start from an up-to-date main

git checkout main
git pull
This way your branch starts from the latest code, not from last week's.

2. Create a branch for one task

git checkout -b feature/shap-endpoint
- -b creates the branch and switches to it in one step.
- Name branches after what they do: feature/... for new work, fix/... for bug fixes, docs/... for documentation.
- One branch per task. Small branches are easier to review and less likely to conflict.

3. Do your work and commit as you go

git status
git add backend/app/api/predict.py
git commit -m "Add SHAP explanation to predict endpoint"
Commit whenever a small piece works. Several small commits are easier to follow than one huge one.

4. Push the branch to GitHub

git push -u origin feature/shap-endpoint
- -u links your local branch to the one on GitHub. After that first push, plain git push works.
- Pushing a branch doesn't touch main, so it's safe to push unfinished work as a backup.

5. Open the pull request

1. Go to the repo on GitHub. A yellow banner usually appears saying "feature/shap-endpoint had recent pushes — Compare & pull request." Click it.
   - If the banner isn't there: Pull requests tab → New pull request → set base: main and compare: your branch.
2. Write a clear title, like "Add SHAP explanations to /predict."
3. In the description, cover:
   - What changed
   - Why it changed
   - How to test it, for example "run uvicorn, POST to /predict, check the shap_values field"
4. Add a groupmate as a Reviewer using the right sidebar.
5. Click Create pull request.

6. Review

- The reviewer opens the Files changed tab, leaves comments on specific lines, then chooses Approve or Request changes.
- To fix something they flagged, commit to the same branch and push again. The PR updates automatically, so you never need to open a new one.

7. Merge

- Once it's approved, click Merge pull request on GitHub.
- GitHub then offers to Delete branch. Accept it, since the work is now in main.

8. Clean up locally and start the next task

git checkout main
git pull
git branch -d feature/shap-endpoint
Then go back to step 2 for the next task