# GitHub Secrets Setup

To enable CI/CD functionality, you need to configure the following secrets in your GitHub repository:

## Required Secrets

### 1. PYPI_API_TOKEN
For automatic publishing to PyPI.

**How to get it:**
1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Add it to GitHub repository secrets:
   - Repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI token

## Optional Secrets

### 2. CODECOV_TOKEN
For code coverage reporting.

**How to get it:**
1. Go to https://codecov.io/gh/TectopiaPeru/yachai-common
2. Connect your repository
3. Get the upload token from repository settings
4. Add it as `CODECOV_TOKEN` in GitHub secrets

## Workflow Permissions

Make sure your Actions have the following permissions:
- Contents: Read and write
- Pull requests: Read and write
- Actions: Read (for self-hosted runners if needed)

## Testing the Setup

1. Push a change to main branch
2. Check Actions tab in GitHub
3. Verify all tests pass
4. Create a tag to test publishing:
   ```bash
   git tag v1.0.0-test
   git push origin v1.0.0-test
   ```

## Note

The first release will be published to TestPyPI by default. To publish to production PyPI:
1. Ensure version is not pre-release
2. The workflow will automatically detect and publish to production
