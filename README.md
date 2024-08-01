# CastorDataBridge - Survey Inviter

## Overview

CastorDataBridge - Survey Inviter is a tool designed to streamline the process of sending out survey invitations using Castor EDC. This guide outlines the steps required to set up and use the tool effectively.

## Table of Contents

1. [Creating CSV Files](#step-1-create-csv-files)
2. [Tag Usage](#step-2-tag-usage)
3. [API Credentials](#step-3-api-credentials)
4. [Email Body Format](#step-4-email-body-format)
5. [Output Files](#step-5-output-files)
6. [Developer Guide](#developer-guide)   
8. [Getting Help](#getting-help)

---

## Step 1: Create CSV Files

### CSV-A: Participant Information
Create a CSV file (`CSV-A`) containing participant details:
- `participant_id`
- `email_address`
- Additional tags for email body

**Example**: `test_file.csv` in the `examples` folder.

### CSV-B: Email Header Information
Create another CSV file (`CSV-B`) with email header details:
- Subject
- Body

**Example**: `header_file.csv` in the `examples` folder.

**Note**: Both CSV files should be encoded as "UTF-8" or "ISO-8859-1".

---

## Step 2: Tag Usage

The tool matches tags from the "Body" column in `CSV-B` with headers in `CSV-A`. It performs case-insensitive matching, replaces spaces with underscores, and searches for a corresponding name in `CSV-B`.

---

## Step 3: API Credentials

Retrieve the Castor EDC API Client ID and Client Secret. The user obtaining these credentials must have “Participant Creation” rights in Castor EDC, which the tool needs to create new Participant IDs mentioned in `CSV-A`.

---

## Step 4: Email Body Format

Format your email body using "\n\n" for line breaks. 

**Example**: `header_file.csv` in the `examples` folder.

---

## Step 5: Output Files

After running the tool, you'll get two output files:
- `output/survey_package_invitations_[current_date].csv`: List of sent surveys.
- `output/survey_invite_results_[current_date].csv`: Error logs, if any.

---

## Developer guide
### Style Guide
This application is formatted using the [Black](https://github.com/psf/black) formatter. Please use this before submitting any code changes.

### Standalone application

It's possible to create a standalone executable (application) with [PyInstaller](https://pyinstaller.org/en/stable/). 
To create this standalone application all you need to do is run two commands. 
The first command is needed to create a `.spec` file. This can be seen as a configuration file.
Here's an example of how to create such a file with pyinstaller:

```python
pyinstaller --onefile --add-data "help_icon.png;." api_call.py get_API_access_token.py get_site_list.py get_survey_list.py get_survey_package_list.py GUI_helper_functions.py GUI_module.py helper_functions.py log_handling.py send_survey_invite.py
```

This will create a `.spec` file called `api_call.spec` (because it's the first Python script mentioned in the commands above).
You can find an example `.spec` file [here](/examples/api_call.spec).
When desired, one can adjust one of the `.spec` file parameters.

If and once these parameters are adjusted, you can create the executable by running: 
```python
pyinstaller api_call.spec
```

This will create a new folder within your Python work environment called "dist".
You can run the application by simply executing the newly created `.exe` file. 
When executing the `.spec` file with the `pyinstaller` command, a new file with the `.exe` extention will be created in the aforementioned folder.


### Package development
- Branching
  - When creating a new branch, please use the following convention: `<issue_number>_<description>_<author_name>`.
- Pull Requests
  - When creating a pull request, please use the following convention: `<type>: <description>`. Example _types_ are `fix:`, `feat:`, `build:`, `chore:`, `ci:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`, and others based on the [Angular convention](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines).

## Getting help

In the case an error occurs when using CastorDataBridge an error log is created. The Research Data Management team of Amsterdam UMC (rdm@amsterdamumc.nl) may ask you to provide this log in helping to fix the error. Please find some actions/checks you can do yourself when unexpected behavior from the application occurs. 


