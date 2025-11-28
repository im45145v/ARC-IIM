# Security Checklist

## ✅ Your Repository is Now Protected!

Your `.gitignore` file is configured to protect:
- ✅ `.env` files (passwords, API keys)
- ✅ `cookies/` directory (LinkedIn session cookies)
- ✅ Database files
- ✅ Log files
- ✅ Temporary files

---

## 🔒 Protected Files

These files will **NEVER** be committed to git:

| File/Directory | Contains | Risk Level |
|----------------|----------|------------|
| `.env` | Database passwords, API keys, LinkedIn credentials | 🔴 CRITICAL |
| `cookies/` | LinkedIn session cookies | 🔴 CRITICAL |
| `*.db`, `*.sqlite` | Database files with personal data | 🟠 HIGH |
| `*.log` | May contain sensitive information | 🟡 MEDIUM |
| `__pycache__/` | Compiled Python files | 🟢 LOW |

---

## 🛡️ Security Check

Run this command anytime to verify your security:

```bash
bash scripts/check_security.sh
```

This checks:
- ✅ `.gitignore` exists
- ✅ Sensitive files are ignored
- ✅ No sensitive files are tracked
- ✅ No credentials in git history

---

## ⚠️ Before Every Commit

**Always run:**

```bash
# Check what you're about to commit
git status

# Verify no sensitive files
bash scripts/check_security.sh

# If all clear, commit
git add .
git commit -m "Your message"
```

---

## 🚨 If You Accidentally Commit Sensitive Files

### Step 1: Remove from staging (before push)

```bash
# Remove from staging but keep the file
git rm --cached .env
git rm --cached -r cookies/

# Commit the removal
git commit -m "Remove sensitive files"
```

### Step 2: Remove from history (after push)

If you already pushed, you need to remove from history:

```bash
# Install git-filter-repo
pip install git-filter-repo

# Remove .env from all history
git filter-repo --path .env --invert-paths

# Remove cookies/ from all history
git filter-repo --path cookies/ --invert-paths

# Force push (WARNING: rewrites history)
git push origin --force --all
```

**⚠️ WARNING:** This rewrites git history. Coordinate with your team!

---

## 📋 What's in Your .gitignore

Your `.gitignore` protects:

### Critical Security
- `.env`, `.env.local`, `.env.*.local`
- `cookies/`, `*.cookies.json`
- `*.pem`, `*.key` (SSH keys)
- `*.crt`, `*.cer` (SSL certificates)

### Python
- `__pycache__/`, `*.pyc`
- `.venv/`, `venv/`, `env/`
- `.pytest_cache/`, `.hypothesis/`

### IDEs
- `.vscode/`, `.idea/`
- `*.sublime-project`

### OS Files
- `.DS_Store` (macOS)
- `Thumbs.db` (Windows)

### Project Files
- `*.log`, `logs/`
- `*.db`, `*.sqlite`
- `scraped_data/`, `pdfs/`

---

## 🔐 Best Practices

### ✅ Do:
1. **Always check** `git status` before committing
2. **Run security check** before pushing
3. **Use `.env.example`** for documentation (no real credentials)
4. **Rotate credentials** if accidentally exposed
5. **Use different credentials** for dev/staging/production

### ❌ Don't:
1. **Never commit** `.env` files
2. **Never commit** cookies or session tokens
3. **Never commit** database files with real data
4. **Never commit** API keys or passwords
5. **Never share** `.env` files via email/chat

---

## 🔄 Regular Maintenance

### Weekly:
- [ ] Review `git status` for unexpected files
- [ ] Check `.env` is not tracked: `git ls-files .env`

### Monthly:
- [ ] Rotate LinkedIn cookies (re-export)
- [ ] Review `.gitignore` for new sensitive files
- [ ] Run security audit: `bash scripts/check_security.sh`

### Before Production:
- [ ] Verify no credentials in code
- [ ] Check all environment variables are in `.env`
- [ ] Confirm `.gitignore` is comprehensive
- [ ] Run security check one final time

---

## 📖 Related Documentation

- **Setup Guide:** [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Cookie Auth:** [docs/COOKIE_AUTHENTICATION.md](docs/COOKIE_AUTHENTICATION.md)
- **Environment Config:** [.env.example](.env.example)

---

## 🆘 Emergency: Credentials Exposed

If you accidentally commit and push credentials:

### Immediate Actions:
1. **Rotate all credentials immediately**
   - Change database passwords
   - Regenerate API keys
   - Re-export LinkedIn cookies
   - Update B2 storage keys

2. **Remove from git history**
   ```bash
   git filter-repo --path .env --invert-paths
   git push origin --force --all
   ```

3. **Notify your team** if working with others

4. **Monitor for unauthorized access**
   - Check database logs
   - Review B2 storage access logs
   - Monitor LinkedIn account activity

### Prevention:
- Set up pre-commit hooks
- Use git-secrets or similar tools
- Enable branch protection rules
- Require code reviews

---

## ✅ Current Status

Run this to check your current security status:

```bash
bash scripts/check_security.sh
```

Expected output:
```
✅ All security checks passed!
   Your sensitive files are protected.
```

---

## 📞 Need Help?

If you're unsure about security:
1. Run the security check script
2. Review this checklist
3. Check the documentation
4. When in doubt, don't commit!

**Remember:** It's easier to prevent exposure than to fix it after! 🔒
