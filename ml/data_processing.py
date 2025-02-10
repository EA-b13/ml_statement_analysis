import os
import re
import pandas as pd
import camelot
from datetime import datetime
import pytesseract
from PIL import Image
import pdf2image

def extract_transactions(file_path):
    """
    Detect file type and extract transactions.
    Returns a list of dictionaries with keys: 'date' (YYYY-MM-DD), 'amount' (float),
    'description' (string) and 'type' ('deposit' or 'withdrawal').
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in ['.csv', '.xls', '.xlsx']:
        transactions = process_csv_excel(file_path)
    elif ext == '.pdf':
        transactions = process_pdf(file_path)
        # Fallback to OCR if no table was found
        if not transactions:
            transactions = process_pdf_ocr(file_path)
    else:
        raise ValueError("Unsupported file format: {}".format(ext))
    
    # Remove any transactions missing a parsed date or amount
    cleaned = [tx for tx in transactions if tx.get('amount') is not None and tx.get('amount') != 0.0]
    return cleaned

def process_csv_excel(file_path):
    """
    Process CSV/Excel file using pandas.
    Looks for common column names like 'date', 'description', 'debit', 'credit',
    as well as alternative columns such as 'in' and 'out' (used in some statements).
    """
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        print("Error reading file:", e)
        return []
    
    # Normalize column names: lower case and strip whitespace
    df = df.rename(columns=lambda x: x.strip().lower())
    
    # Heuristic mapping for common column names:
    col_map = {
        'date': None,
        'description': None,
        'debit': None,
        'credit': None,
        'in': None,
        'out': None,
        'amount': None
    }
    for col in df.columns:
        col_l = col.lower()
        if not col_map['date'] and "date" in col_l:
            col_map['date'] = col
        if not col_map['description'] and any(k in col_l for k in ['particular', 'merchant', 'description']):
            col_map['description'] = col
        if not col_map['debit'] and "debit" in col_l:
            col_map['debit'] = col
        if not col_map['credit'] and "credit" in col_l:
            col_map['credit'] = col
        if not col_map['in'] and (col_l.strip() == "in" or " in" in col_l):
            col_map['in'] = col
        if not col_map['out'] and (col_l.strip() == "out" or " out" in col_l):
            col_map['out'] = col
        if not col_map['amount'] and "amount" in col_l:
            col_map['amount'] = col

    transactions = []
    for _, row in df.iterrows():
        date_raw = row.get(col_map['date'], '')
        try:
            date_val = standardize_date(str(date_raw))
        except Exception as e:
            continue  # skip rows without a valid date
        
        # Determine the amount based on available columns.
        amount = 0.0
        if col_map['debit'] or col_map['credit']:
            debit_val = parse_numeric(row.get(col_map['debit'], 0)) if col_map['debit'] else 0.0
            credit_val = parse_numeric(row.get(col_map['credit'], 0)) if col_map['credit'] else 0.0
            amount = credit_val - debit_val
        elif col_map['in'] or col_map['out']:
            deposit = parse_numeric(row.get(col_map['in'], 0)) if col_map['in'] else 0.0
            withdrawal = parse_numeric(row.get(col_map['out'], 0)) if col_map['out'] else 0.0
            amount = deposit - withdrawal
        elif col_map['amount']:
            amount = parse_numeric(row.get(col_map['amount'], 0))
        
        description = row.get(col_map['description'], '') if col_map['description'] else ''
        tx_type = categorize_transaction(amount, description)
        
        transactions.append({
            'date': date_val,
            'amount': amount,
            'description': normalize_description(str(description)),
            'type': tx_type
        })
    return transactions

def process_pdf(file_path):
    """
    Process a PDF file page-by-page using Camelot with the following logic:
      1. For each table on a page, compute a header score for each row based on the occurrence
         of keywords from header_keywords. A row scoring >= 3 is considered the header row.
         Additionally, if a header cell contains both "date" and ("transaction" or "particular"),
         that column is marked as "date_transaction".
      2. Process all rows below the header as transaction rows.
      3. Process one page at a time. For pages > 1, if the first row of the first table matches the
         last row of the previous page’s last table, treat this table as a continuation (use previous header).
      4. For each transaction row, if the field from a "date_transaction" column is encountered,
         attempt to split it into a date and description.
      5. If a row does not contain any amount but has a description, and the following row provides an amount,
         merge those rows so that the final transaction uses the date from the first row, the combined description,
         and the amount from the next row.
    Returns a list of transaction dictionaries.
    """
    import camelot
    import pdf2image
    import re

    transactions = []
    header_keywords = ['date', 'transaction', 'description', 'debit', 'credit', 'balance', 'amount', 'in', 'out']

    # Get total number of pages from the PDF.
    try:
        info = pdf2image.pdfinfo_from_path(file_path)
        total_pages = int(info.get("Pages", 1))
    except Exception as e:
        print("Error getting PDF info:", e)
        total_pages = 1

    prev_last_row = None
    prev_header = None

    # Process pages one at a time.
    for page in range(1, total_pages + 1):
        try:
            tables = camelot.read_pdf(file_path, pages=str(page), flavor='stream')
        except Exception as e:
            print(f"Error reading page {page} with Camelot:", e)
            continue

        for i, table in enumerate(tables):
            df = table.df
            if df.empty or df.shape[0] < 2:
                continue
            
            print(df)
            # Convert rows to a list of lists; also build a normalized version (lowercase)
            rows = df.values.tolist()
            normalized_rows = [[str(cell).strip().lower() for cell in row] for row in rows]

            # Check for multi-page continuation on the first table of the page.
            is_continuation = False
            if page > 1 and i == 0 and prev_last_row is not None:
                first_row = normalized_rows[0]
                if len(first_row) == len(prev_last_row):
                    # Uncomment the following if you wish to require an exact match:
                    # if all(a == b for a, b in zip(first_row, prev_last_row)):
                    is_continuation = True

            header_idx = None
            header = None

            if is_continuation and prev_header is not None:
                header = prev_header
                header_idx = -1  # Marker: no new header in this table.
            else:
                # Look for a header row by scoring each row.
                for idx, row in enumerate(normalized_rows):
                    matched_keywords = set()
                    for cell in row:
                        for kw in header_keywords:
                            if kw in cell:
                                matched_keywords.add(kw)
                    if len(matched_keywords) >= 3:
                        header_idx = idx
                        header = [str(cell).strip() for cell in rows[idx]]
                        break

            if header is None:
                continue  # Skip this table if no header is found.

            # Build column mapping using header.
            # Also detect if any header cell combines date and transaction info.
            col_map = {}
            pattern_date_transaction = re.compile(r"\bdate\s+transaction\b", re.IGNORECASE)
            for j, col_name in enumerate(header):
                col_lower = col_name.lower()
                date_transaction_matches = pattern_date_transaction.findall(col_lower)
                if len(date_transaction_matches)>0:
                    col_map[j] = "date_transaction"
                    print("Got date_transaction")
                elif "date" in col_lower:
                    col_map[j] = "date"
                elif any(x in col_lower for x in ['description', 'particular', 'merchant']):
                    col_map[j] = "description"
                elif any(x in col_lower for x in ['debit', 'out']):
                    col_map[j] = "debit"
                elif any(x in col_lower for x in ['credit', 'in']):
                    col_map[j] = "credit"
                elif "amount" in col_lower:
                    col_map[j] = "amount"
                elif "balance" in col_lower:
                    col_map[j] = "balance"
                else:
                    col_map[j] = None

            # Determine data rows.
            if header_idx == -1:
                data_rows = rows  # Continuation table: use all rows.
            else:
                data_rows = rows[header_idx + 1:]

            # Process each data row using a while-loop to allow merging.
            i_row = 0
            while i_row < len(data_rows):
                row = data_rows[i_row]
                row_data = {}
                # Build row_data using col_map.
                for j, cell in enumerate(row):
                    field = col_map.get(j)
                    if field:
                        row_data[field] = cell.strip()

                # If a "date_transaction" field is present, try splitting it.
                if "date_transaction" in row_data:
                    # Use a regex pattern: match a date (e.g., "01 Dec" optionally followed by a year)
                    # then the remainder is the transaction description.
                    pattern = r'^(\d{1,2}\s+[A-Za-z]{3}(?:\s+\d{2,4})?)(.*)$'
                    m = re.match(pattern, row_data["date_transaction"])
                    if m:
                        row_data["date"] = m.group(1).strip()
                        # Append any text after the date to the description.
                        row_data["description"] = m.group(2).strip()
                    else:
                        row_data["description"] = row_data["date_transaction"]

                # Helper: determine if row_data has an amount (from debit, credit, or amount fields).
                def has_amount(data):
                    debit = parse_numeric(data.get("debit", "0"))
                    credit = parse_numeric(data.get("credit", "0"))
                    amt = parse_numeric(data.get("amount", "0"))
                    return (debit != 0 or credit != 0 or amt != 0)

                current_has_amt = has_amount(row_data)
                current_desc = row_data.get("description", "")

                # Merging logic: if current row has a description but no amount, look ahead
                # and if the next row provides an amount, merge them.
                if (not current_has_amt) and current_desc and (i_row + 1 < len(data_rows)):
                    next_row = data_rows[i_row + 1]
                    next_data = {}

                    for j, cell in enumerate(next_row):
                        field = col_map.get(j)
                        if field:
                            next_data[field] = cell.strip()
                    next_has_amt = has_amount(next_data)
                    next_desc = next_data.get("description", "")

                    if next_has_amt and (not next_desc or next_desc == ""):
                        merged_desc = current_desc

                        # Determine merged amount.
                        debit_val = parse_numeric(next_data.get("debit", "0"))
                        credit_val = parse_numeric(next_data.get("credit", "0"))
                        if debit_val != 0 or credit_val != 0:
                            merged_amt = credit_val - debit_val
                        elif "amount" in next_data:
                            merged_amt = parse_numeric(next_data["amount"])
                        else:
                            merged_amt = 0.0
                        try:
                            std_date = standardize_date(row_data.get("date", ""))
                        except Exception:
                            std_date = None
                        transactions.append({
                            'date': std_date,
                            'amount': merged_amt,
                            'description': merged_desc,
                            'type': categorize_transaction(merged_amt, merged_desc, row_data.get("debit"), row_data.get("credit"))
                        })
                        i_row += 2  # Skip the next row since it has been merged.
                        continue

                # Process current row normally.
                try:
                    std_date = standardize_date(row_data.get("date", None))
                except Exception:
                    i_row += 1
                    continue

                debit_val = parse_numeric(row_data.get("debit", "0"))
                credit_val = parse_numeric(row_data.get("credit", "0"))
                if debit_val != 0 or credit_val != 0:
                    amt = credit_val - debit_val
                elif "amount" in row_data:
                    amt = parse_numeric(row_data["amount"])
                else:
                    amt = 0.0

                desc = row_data.get("description", "")
                tx_type = categorize_transaction(amt, desc, row_data.get("debit"), row_data.get("credit"))
                transactions.append({
                    'date': std_date,
                    'amount': amt,
                    'description': desc,
                    'type': tx_type
                })
                i_row += 1

            # For multi-page continuation, update prev_last_row and prev_header from this page’s last table.
            if i == len(tables) - 1 and len(data_rows) > 0:
                prev_last_row = normalized_rows[-1]
                prev_header = header

    return transactions

def process_pdf_ocr(file_path):
    """
    Fallback method: Convert each PDF page to an image and use Tesseract OCR.
    Then use a regex to try to pick out a date and an amount from each line.
    """
    transactions = []
    try:
        images = pdf2image.convert_from_path(file_path)
        for image in images:
            text = pytesseract.image_to_string(image)
            transactions.extend(parse_transactions_from_text(text))
    except Exception as e:
        print("Error processing PDF with OCR:", e)
    return transactions

def parse_transactions_from_text(text):
    """
    Very basic line-by-line parsing from OCR text.
    Uses a regex pattern to capture a date (many possible formats) and an amount.
    Note: This is a fallback and may require further tuning.
    """
    transactions = []
    lines = text.splitlines()
    # This regex tries to capture a date and a numeric amount (which may include commas and decimals)
    pattern = re.compile(r'(\d{1,2}[-/\s][A-Za-z]{3,}[-/\s]\d{2,4}).*?([-\d,]+\.\d{2})')
    for line in lines:
        match = pattern.search(line)
        if match:
            date_str = match.group(1).strip()
            amount_str = match.group(2).strip()
            try:
                date_val = standardize_date(date_str)
                amount = parse_numeric(amount_str)
                tx_type = 'deposit' if amount >= 0 else 'withdrawal'
                description = normalize_description(line.replace(date_str, '').replace(amount_str, ''))
                transactions.append({
                    'date': date_val,
                    'amount': amount,
                    'description': description,
                    'type': tx_type
                })
            except Exception:
                continue
    return transactions

def standardize_date(date_str):
    """
    Convert a date string into ISO format (YYYY-MM-DD).
    Tries several common formats (including ones seen in the sample statements).
    """
    date_str = date_str.strip()
    date_str = re.sub(r'[,\*]', '', date_str)
    date_formats = [
        '%d-%b-%Y', '%d %b %Y', '%d-%b-%y', '%d %b %y', 
        '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y',
        '%d %B %Y', '%d-%B-%Y',
        '%d %b.%Y', '%d %b. %Y',
        '%d %b%y'
    ]
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except Exception:
            continue
    raise ValueError(f"Date format not recognized: {date_str}")

def categorize_transaction(amount, description, debit = None, credit = None):
    """
    Simple categorization: if the amount is positive, label it as a deposit; if negative, a withdrawal.
    If zero, attempt to infer from keywords in the description.
    """
    # desc = description.lower()
    # if debit is not None and debit != "" and debit:
    #     return "withdrawal"
    # elif credit is not None and credit != "":
    #     return "deposit"

    # if "deposit" in desc or "credit" or "in" in desc:
    #     return "deposit"
    # elif "withdrawal" in desc or "debit" or "out" in desc:
    #     return "withdrawal"
    # else:
    if amount > 0:
        return "deposit"
    elif amount < 0:
        return "withdrawal"
    
    return "unknown"

def normalize_description(description):
    """
    Clean up extra whitespace and return title-cased description.
    """
    if not description:
        return ""
    return " ".join(description.split()).title()

def parse_numeric(value):
    """
    Convert a string (or number) to float. Removes commas and other extraneous characters.
    """
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    value = str(value).replace(',', '').strip()
    try:
        return float(value)
    except ValueError:
        return 0.0