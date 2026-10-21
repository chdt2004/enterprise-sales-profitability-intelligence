# Put the extracted project on GitHub

Do this from the extracted `enterprise-intelligence` folder, containing README.md. Never upload your SAP credentials, .env, tenant URLs with tokens, or .venv. The provided .gitignore excludes common local files and the generated SQLite database; CSVs are intentionally committed because these are small synthetic data.

## Fast browser route: no Git installation needed

1. Sign in to GitHub, click New repository.
2. Name: `enterprise-sales-demand-intelligence`. Description: `Python, SQL, SAP Datasphere and SAC commercial analytics portfolio using synthetic data`.
3. Select Public if you want recruiters to access it. Create an empty repository (don't precreate a README).
4. Choose “uploading an existing file” / Add file → Upload files.
5. Drag **the extracted folder contents**, preserving src/, data/, docs/, datasphere/, notebooks/, sql/, outputs/, plus README.md, START_HERE.md and requirements.txt. Don't drag the ZIP or .venv. Browser upload limits apply; use Git if the browser refuses folders. Hidden .gitignore may need separate selection or the Git route.
6. Commit with `Add enterprise sales and demand intelligence project`.
7. Open README on GitHub and verify folders/files render. Copy repository URL to your CV.

## Git terminal route

Install Git if `git --version` is unavailable. Create an empty GitHub repository as above first. Replace YOUR_USERNAME in the remote URL. Copy one line at a time:

```bash
git init
git branch -M main
git add .
git status
git commit -m "Add enterprise sales profitability and demand intelligence project"
git remote add origin https://github.com/YOUR_USERNAME/enterprise-sales-demand-intelligence.git
git push -u origin main
```

Git may ask you to sign in through a browser or credential manager. Do not use your account password as a token and do not paste tokens into source files.

If Git asks for identity:

```bash
git config user.name "YOUR NAME"
git config user.email "YOUR GITHUB EMAIL OR GITHUB NOREPLY ADDRESS"
git commit -m "Add enterprise sales profitability and demand intelligence project"
git push -u origin main
```

If a remote already exists, inspect `git remote -v` before changing it. If the repository already contains files, clone it into a new folder and copy this project into that checkout before adding/committing; don't force-push or overwrite unrelated history.

## After building SAP

Add sanitized screenshots to evidence/ and update README with the true deployment status and integration route. Then:

```bash
git add README.md evidence
git commit -m "Add SAP deployment evidence"
git push
```

Only run this last block after the evidence folder exists. No GitHub repository has been created by this project pack; these commands run under your account.
