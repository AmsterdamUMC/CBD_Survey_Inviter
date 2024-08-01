# CastorDataBridge - Survey Invite

## Overview

CastorDataBridge - Survey Invite is a tool designed to streamline the process of sending out survey invitations using Castor EDC. This guide outlines the steps required to set up and use the tool effectively.

## Table of Contents

1. [Creating CSV Files](#step-1-create-csv-files)
2. [Tag Usage](#step-2-tag-usage)
3. [API Credentials](#step-3-api-credentials)
4. [Email Body Format](#step-4-email-body-format)
5. [Output Files](#step-5-output-files)
6. [Troubleshooting](#troubleshooting)

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
- `survey_package_invitations_[current_date].csv`: List of sent surveys.
- `survey_invite_results_[current_date].csv`: Error logs, if any.

---

## Troubleshooting

If you encounter issues or need further assistance, please send a mail to rdm@amsterdamumc.nl.
