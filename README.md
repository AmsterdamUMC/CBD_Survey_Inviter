# CBD_Survey_Invite

# Tool Usage Instructions

## Step 1: Create CSV Files

1. Create two CSV files:
    - **CSV-A**: Contains participant information, such as `participant_id`, `email_address`, and any additional tags you wish to include in the email body. For reference, see `test_file.csv` in the `examples` folder.
    - **CSV-B**: Contains email header information, including the Subject and Body. For reference, see `header_file.csv` in the `examples` folder.

## Step 2: Tag Usage

The tool reads tags provided in the “Body” column of CSV-B. It matches these tags with the headers in CSV-A by adjusting the casing to be case-insensitive, replacing spaces with underscores, and finding a matching name in the “Body” column of CSV-B.

## Step 3: API Credentials

To use the tool, you need to fetch the API Client ID and Client Secret. Ensure that the user fetching these credentials has “Participant Creation” rights in Castor EDC. The tool requires these rights to create any Participant IDs mentioned in CSV-A that do not exist in Castor EDC.

## Step 4: Email Body Format

Paste the desired email body in the correct format, ensuring there are no extra characters or formatting issues.

## Step 5: Output Files

Upon completion of the tool's execution, two output files are generated:
- `survey_package_invitations_[current_date].csv`
- If errors occurred, `survey_invite_results_[current_date].csv`
