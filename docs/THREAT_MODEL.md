# Threat Model — FinSight AI

**Version:** 1.0  
**Date:** 2026-10-17

## 1. Assets to Protect

### Critical
- **Financial transaction data:** Income, expenses, amounts, dates, descriptions
- **Account balances:** Current and historical
- **User credentials:** Passwords, session tokens
- **Personal information:** Names, emails

### High Value
- **Budget data:** Spending limits, financial goals
- **CSV imports:** Bank/bookkeeping data files
- **Forecast scenarios:** Financial planning data
- **Audit logs:** Who did what when

## 2. Trust Boundaries

```
┌─────────────────────────────────────────┐
│ User's Browser (Untrusted)              │
│ - Input validation client-side only     │
│ - Display logic                          │
└──────────────┬──────────────────────────┘
               │ HTTPS
               │ (Trust Boundary #1)
┌──────────────▼──────────────────────────┐
│ Backend API (Trusted)                   │
│ - Authentication                         │
│ - Authorization                          │
│ - Input validation (authoritative)      │
│ - Business logic                         │
└──────────────┬──────────────────────────┘
               │ Encrypted connection
               │ (Trust Boundary #2)
┌──────────────▼──────────────────────────┐
│ Database (Trusted)                      │
│ - Data at rest                           │
│ - Constraints enforce integrity         │
└─────────────────────────────────────────┘

External (Untrusted):
┌─────────────────────────────────────────┐
│ AI Provider API (Optional)              │
│ - Receives anonymized summaries only    │
│ - Timeout protection                     │
└─────────────────────────────────────────┘
```

## 3. Threat Categories (STRIDE)

### 3.1 Spoofing Identity

**Threat:** Attacker impersonates legitimate user.

**Attack Vectors:**
- Stolen credentials (phishing, keylogger)
- Session hijacking (XSS, network sniffing)
- Weak passwords

**Mitigations:**
- Password hashing (bcrypt/argon2, cost factor 12+)
- HTTPS only (no plain HTTP)
- HTTP-only cookies for session tokens
- Secure flag on cookies
- Session expiry (1 hour access, 7 days refresh)
- Rate limiting on login attempts (5 attempts per 15 min)
- Email confirmation for new devices (future)
- 2FA support (future)

**Validation:**
- Test: Stolen token from different IP rejected (future)
- Test: Expired token rejected
- Test: Password hash never returned in API response

### 3.2 Tampering with Data

**Threat:** Attacker modifies transactions, balances, or reports.

**Attack Vectors:**
- SQL injection
- Direct database access
- API manipulation (change other users' data)
- CSV injection in exports

**Mitigations:**
- Parameterized queries (SQLAlchemy ORM)
- Authorization checks on every endpoint
- Workspace isolation enforced in queries
- Input validation (Pydantic schemas)
- Database constraints (CHECK, FOREIGN KEY)
- Audit logging (immutable)
- CSV export: escape formulas (prefix =, +, -, @ with ')
- Read-only database user for reporting (future)

**Validation:**
- Test: User A cannot modify User B's transaction (403)
- Test: SQL injection in description field sanitized
- Test: CSV export with `=SUM(A1:A10)` becomes `'=SUM(A1:A10)`
- Test: Audit log records all transaction changes

### 3.3 Repudiation

**Threat:** User denies performing financial action.

**Attack Vectors:**
- No audit trail
- Shared accounts
- Missing timestamps

**Mitigations:**
- Audit log for all financial operations
- Immutable audit table (no UPDATE/DELETE)
- Timestamp with timezone on all records
- User ID associated with every change
- IP address logging (optional, privacy-aware)

**Validation:**
- Test: Transaction creation logged with user_id and timestamp
- Test: Audit log cannot be modified or deleted

### 3.4 Information Disclosure

**Threat:** Unauthorized access to financial data.

**Attack Vectors:**
- Cross-workspace data leakage
- API response includes other users' data
- Error messages expose internal details
- Logs contain sensitive data
- Unencrypted backups
- AI provider sees full transaction details

**Mitigations:**
- Authorization on every endpoint (workspace membership check)
- Filter queries by workspace_id
- Generic error messages ("Not found" not "Transaction belongs to workspace X")
- Redact sensitive data from logs
- Encrypt database backups
- HTTPS for all connections
- No transaction details to AI provider (anonymized summaries only)
- Database encryption at rest (future)
- Sensitive columns encrypted (future: per-column encryption for descriptions)

**Validation:**
- Test: User A queries User B's transaction ID → 404 (not 403)
- Test: Error response does not include SQL query
- Test: Application logs do not contain transaction amounts
- Test: AI insight request excludes PII (names, account numbers)

### 3.5 Denial of Service

**Threat:** Attacker makes application unavailable.

**Attack Vectors:**
- API spam (high request rate)
- Large CSV upload
- Expensive queries (unindexed filters)
- Recursive import loops

**Mitigations:**
- Rate limiting (100 requests per minute per user)
- File upload size limit (10 MB)
- CSV row limit (10,000 rows per import)
- Query timeouts (10 seconds)
- Database indexes on frequent queries
- Pagination (max 100 per page)
- Background jobs for slow tasks (future)

**Validation:**
- Test: 101st request in 1 minute → 429 Too Many Requests
- Test: 11 MB CSV upload rejected
- Test: 20,000-row CSV rejected with error message

### 3.6 Elevation of Privilege

**Threat:** Attacker gains admin/owner access without authorization.

**Attack Vectors:**
- Missing authorization checks
- Role-based access control bypass
- Workspace membership manipulation
- JWT tampering

**Mitigations:**
- Authorization middleware on all protected endpoints
- Role enforcement in database queries
- JWT signed with strong secret (256-bit)
- No client-side role checks (backend is authoritative)
- Principle of least privilege

**Validation:**
- Test: User with 'viewer' role cannot create transactions (future roles)
- Test: User cannot add themselves to another workspace
- Test: Tampered JWT rejected (signature verification)

## 4. Specific Attack Scenarios

### 4.1 SQL Injection

**Attack:**
```python
# Vulnerable (DON'T DO THIS)
query = f"SELECT * FROM transactions WHERE description = '{user_input}'"
# Attacker input: "'; DROP TABLE transactions; --"
```

**Defense:**
```python
# Safe (SQLAlchemy ORM)
transactions = db.query(Transaction).filter(
    Transaction.description == user_input
).all()
```

**Test:**
```python
def test_sql_injection():
    malicious_input = "'; DROP TABLE transactions; --"
    response = client.post("/api/transactions", json={
        "description": malicious_input,
        "amount": 100,
        "type": "expense",
    })
    assert response.status_code == 201
    # Verify tables still exist
    assert db.query(Transaction).count() == 1
```

### 4.2 Cross-Workspace Data Leakage

**Attack:** User A requests User B's transaction by guessing UUID.

**Defense:**
```python
@app.get("/api/transactions/{transaction_id}")
def get_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    txn = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.workspace_id.in_(current_user.workspace_ids)  # Authorization
    ).first()
    
    if not txn:
        raise HTTPException(status_code=404, detail="Not found")  # Generic
    
    return txn
```

**Test:**
```python
def test_cross_workspace_access():
    user_a_token = login_as_user_a()
    user_b_transaction_id = create_transaction_for_user_b()
    
    response = client.get(
        f"/api/transactions/{user_b_transaction_id}",
        headers={"Authorization": f"Bearer {user_a_token}"}
    )
    assert response.status_code == 404  # Not 403 (don't confirm existence)
```

### 4.3 CSV Formula Injection

**Attack:** Malicious description in CSV export triggers formula execution in Excel.

**Scenario:**
```csv
Date,Description,Amount
2026-10-17,=1+1,100.00  # Opens calculator
2026-10-17,=HYPERLINK("http://evil.com"),50.00  # Phishing
```

**Defense:**
```python
def escape_csv_formula(value: str) -> str:
    """Escape potential formulas in CSV exports."""
    if value and value[0] in ("=", "+", "-", "@"):
        return "'" + value  # Prefix with single quote
    return value

def export_to_csv(transactions: List[Transaction]) -> str:
    rows = []
    for t in transactions:
        rows.append([
            t.transaction_date.isoformat(),
            escape_csv_formula(t.description),
            str(t.amount),
        ])
    return csv_writer.write(rows)
```

**Test:**
```python
def test_csv_injection_prevention():
    transaction = Transaction(description="=1+1", amount=100)
    csv_output = export_to_csv([transaction])
    assert "'=1+1" in csv_output  # Escaped
```

### 4.4 Excessive AI Data Exposure

**Attack:** AI provider receives full transaction history with PII.

**Defense:**
```python
def generate_insight(transactions: List[Transaction]) -> str:
    # Anonymize before sending to AI
    summary = {
        "total_income": sum(t.amount for t in transactions if t.type == "income"),
        "total_expense": sum(t.amount for t in transactions if t.type == "expense"),
        "category_totals": aggregate_by_category(transactions),
        # NO: descriptions, account names, user names
    }
    
    prompt = f"Analyze spending: {summary}"
    return ai_client.generate(prompt, timeout=10)
```

**Test:**
```python
def test_ai_data_minimization(mocker):
    mock_ai = mocker.patch("ai_client.generate")
    
    transactions = [
        Transaction(description="Salary from Acme Corp", amount=5000, type="income"),
    ]
    
    generate_insight(transactions)
    
    # Verify AI call does not include description
    call_args = mock_ai.call_args[0][0]
    assert "Acme Corp" not in call_args
    assert "5000" in call_args  # Aggregates OK
```

## 5. Data Flow Security

### 5.1 Registration/Login

```
User → Frontend: email, password (HTTPS)
Frontend → Backend: POST /api/auth/register (HTTPS)
Backend: Hash password (bcrypt)
Backend → DB: Store user with password_hash
Backend → Frontend: Success + JWT
Frontend: Store JWT in HTTP-only cookie
```

**Security:**
- Password never stored plain text
- Password never logged
- JWT stored in HTTP-only cookie (not localStorage)

### 5.2 Transaction Creation

```
User → Frontend: amount, date, category, description
Frontend: Validate with Zod
Frontend → Backend: POST /api/transactions (HTTPS, JWT)
Backend: Authenticate (verify JWT)
Backend: Authorize (check workspace membership)
Backend: Validate (Pydantic)
Backend → DB: Insert transaction (parameterized query)
Backend: Log audit event
Backend → Frontend: Created transaction (201)
```

**Security:**
- Double validation (client + server)
- Authorization before any DB write
- Audit trail

### 5.3 CSV Import

```
User → Frontend: Upload CSV file
Frontend → Backend: POST /api/imports/upload (multipart)
Backend: Validate file size (<10 MB)
Backend: Store temp file (non-executable dir)
Backend → Frontend: import_id
User → Frontend: Map columns
Frontend → Backend: POST /api/imports/{id}/preview
Backend: Parse CSV (limit 10k rows)
Backend: Validate each row
Backend: Detect duplicates
Backend → Frontend: Preview with errors
User → Frontend: Confirm import
Frontend → Backend: POST /api/imports/{id}/confirm
Backend: Insert valid rows in DB transaction
Backend: Delete temp file
Backend → Frontend: Summary
```

**Security:**
- File size limit
- Row limit
- Temp file isolation
- Delete after processing
- Transaction rollback on error

## 6. Compliance Considerations

### GDPR (if applicable)
- **Right to access:** Export all user data
- **Right to erasure:** Delete workspace and all associated data
- **Data minimization:** Only collect necessary fields
- **Purpose limitation:** Financial tracking only, no marketing
- **Consent:** AI insights require opt-in

### Financial Data Regulations
- **Not a bank:** No real bank access, no payment execution
- **Not financial advice:** Clear disclaimers
- **Local storage:** Data stays on user's server by default
- **Audit trail:** Immutable logs for accountability

## 7. Security Testing Checklist

- [ ] SQL injection tests on all text inputs
- [ ] Authorization tests: User A cannot access User B's data
- [ ] XSS tests: Script in description field sanitized
- [ ] CSRF tests: State-changing requests require token (if cookie auth)
- [ ] Rate limiting tests: 429 after limit exceeded
- [ ] CSV injection tests: Formulas escaped in exports
- [ ] File upload tests: Reject >10 MB, non-CSV files
- [ ] Password tests: Weak passwords rejected (8+ chars, complexity)
- [ ] Session tests: Expired token rejected
- [ ] Audit log tests: All changes logged
- [ ] Error handling tests: No internal details leaked
- [ ] Penetration test: OWASP ZAP or Burp Suite scan (before prod)

## 8. Incident Response

### Data Breach
1. Identify scope (which workspaces affected)
2. Revoke compromised sessions
3. Force password reset for affected users
4. Notify users within 72 hours (GDPR)
5. Restore from backup if data corrupted
6. Review and fix vulnerability
7. Document incident

### Service Outage
1. Check database connectivity
2. Check application logs
3. Restart services if needed
4. Restore from backup if database corrupted
5. Notify users via status page

## 9. Security Roadmap

**MVP (P0):**
- Authentication (password hashing)
- Authorization (workspace isolation)
- Input validation
- SQL injection prevention
- CSV formula injection prevention
- HTTPS

**Post-MVP (P1):**
- Rate limiting
- Audit logging
- Secure session management
- Error message sanitization

**Future (P2):**
- 2FA
- Database encryption at rest
- Column-level encryption for descriptions
- Security headers (CSP, HSTS)
- Penetration testing
- Bug bounty program

## Next Steps

Begin implementation: accounts and transactions (Phase 5).
