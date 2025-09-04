# Google Sheets Automation Example

Automated filling of Google Sheets cells with complex formatting, multi-line text, and bullet points.

## What it does

The `universal_sheet_filler.py` script can:
- Fill ANY cell in Google Sheets (not just columns)
- Handle multi-line text with proper Alt+Enter breaks
- Support bullet points and formatted text
- Work with existing Chrome sessions

## Setup

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install deps
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

## Usage Examples

### Basic Usage

1. **Launch Chrome with debugging:**
```bash
# From the root directory
python ../../real_chrome_session.py --restart --copy-profile --profile "Profile 2"
```

2. **Navigate to your Google Sheet manually in the browser**

3. **Run the filler with your data:**
```bash
python universal_sheet_filler.py example_data/security_questionnaire_bank.json
```

### Real-World Example: Filling a Security Questionnaire

```bash
# Step 1: Reset Chrome if having issues
python ../../real_chrome_session.py --reset

# Step 2: Launch Chrome with debugging
python ../../real_chrome_session.py --restart --copy-profile --profile "Profile 2"

# Step 3: Open your Google Sheet (e.g., security questionnaire)
# Navigate manually to: https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID

# Step 4: Run the automation
python universal_sheet_filler.py example_data/security_questionnaire_bank.json

# The script will:
# - Fill C2 with "Does your company maintain an Information Security Management System?"
# - Fill C3 with multi-line security policies
# - Continue filling all specified cells
```

### Custom Data Example

Create your own data file `my_answers.json`:
```json
{
  "A1": "Project Title",
  "B2": "Status: In Progress",
  "C3": "Owner: John Doe\nDepartment: Engineering",
  "D4": "• Task 1: Complete\n• Task 2: In Progress\n• Task 3: Pending",
  "E5": "Notes:\n- Review required\n- Deadline: Friday"
}
```

Run it:
```bash
python universal_sheet_filler.py my_answers.json
```

### Filling Multiple Sheets

```bash
# Sheet 1 - Project tracker
python universal_sheet_filler.py project_data.json

# Sheet 2 - Budget (switch tabs manually)
python universal_sheet_filler.py budget_data.json

# Sheet 3 - Timeline (switch tabs manually)  
python universal_sheet_filler.py timeline_data.json
```

## Data Format

The script accepts JSON files with cell addresses as keys:

```json
{
  "C2": "First answer",
  "C3": "Second answer with\nmultiple lines",
  "D5": "• Bullet point 1\n• Bullet point 2",
  "A10": "Any cell address works",
  "AA50": "Even far cells like AA50"
}
```

## Tips & Tricks

1. **Multi-line text**: Use `\n` in your JSON for line breaks
2. **Bullet points**: Start lines with `•` or `-` for lists
3. **Large datasets**: The script handles any number of cells
4. **Error recovery**: If it fails, check Chrome is still running on port 9222
5. **Different profiles**: Use `--profile "Profile Name"` to use different Chrome profiles

## Troubleshooting

```bash
# Chrome won't start?
python ../../real_chrome_session.py --reset

# Port already in use?
python ../../real_chrome_session.py --port 9223

# See available profiles
python ../../real_chrome_session.py --list-profiles
```

## Example Data Files

- `example_data/security_questionnaire_bank.json` - Security questionnaire answers
- `example_data/technical_answers_final.json` - Technical configuration answers