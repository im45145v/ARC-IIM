#!/bin/bash
# Security check script - verifies sensitive files are not tracked by git

echo "🔒 Security Check - Verifying sensitive files are protected"
echo "============================================================"
echo

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .gitignore exists
if [ ! -f .gitignore ]; then
    echo -e "${RED}❌ CRITICAL: .gitignore file not found!${NC}"
    echo "   Run: git init && create .gitignore"
    exit 1
else
    echo -e "${GREEN}✅ .gitignore file exists${NC}"
fi

# Check if sensitive files are ignored
echo
echo "Checking if sensitive files are ignored by git..."
echo

SENSITIVE_FILES=(
    ".env"
    "cookies/"
    "cookies/linkedin_cookies_1.json"
)

ALL_SAFE=true

for file in "${SENSITIVE_FILES[@]}"; do
    if git check-ignore "$file" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $file is ignored${NC}"
    else
        echo -e "${RED}❌ WARNING: $file is NOT ignored!${NC}"
        ALL_SAFE=false
    fi
done

# Check if sensitive files exist and are tracked
echo
echo "Checking if sensitive files are tracked by git..."
echo

if [ -f .env ]; then
    if git ls-files --error-unmatch .env > /dev/null 2>&1; then
        echo -e "${RED}❌ CRITICAL: .env is tracked by git!${NC}"
        echo "   Run: git rm --cached .env"
        ALL_SAFE=false
    else
        echo -e "${GREEN}✅ .env exists but is not tracked${NC}"
    fi
fi

if [ -d cookies ]; then
    if git ls-files cookies/ | grep -q .; then
        echo -e "${RED}❌ CRITICAL: cookies/ directory has tracked files!${NC}"
        echo "   Run: git rm --cached -r cookies/"
        ALL_SAFE=false
    else
        echo -e "${GREEN}✅ cookies/ directory exists but is not tracked${NC}"
    fi
fi

# Check for accidentally committed credentials
echo
echo "Checking for accidentally committed credentials..."
echo

if git log --all --full-history --source --pretty=format: -- .env cookies/ 2>/dev/null | grep -q .; then
    echo -e "${YELLOW}⚠️  WARNING: Sensitive files found in git history!${NC}"
    echo "   These files were committed in the past."
    echo "   Consider using git-filter-repo to remove them:"
    echo "   pip install git-filter-repo"
    echo "   git filter-repo --path .env --invert-paths"
    echo "   git filter-repo --path cookies/ --invert-paths"
    ALL_SAFE=false
else
    echo -e "${GREEN}✅ No sensitive files found in git history${NC}"
fi

# Summary
echo
echo "============================================================"
if [ "$ALL_SAFE" = true ]; then
    echo -e "${GREEN}✅ All security checks passed!${NC}"
    echo "   Your sensitive files are protected."
    exit 0
else
    echo -e "${RED}❌ Security issues found!${NC}"
    echo "   Please fix the issues above before committing."
    exit 1
fi
