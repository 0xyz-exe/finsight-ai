# Forecasting Methodology — FinSight AI

**Version:** 1.0  
**Date:** 2026-10-17  
**Status:** P2 Feature (Post-MVP)

## 1. Core Principle

**Forecasts are projections, not guarantees.** All forecasts clearly labeled, methodology disclosed, assumptions transparent.

## 2. Minimum Data Requirements

- **Simple Average:** 3 months of historical data
- **Trend-Based:** 12 months of historical data
- **Seasonal:** 24 months of historical data (future enhancement)

If insufficient data, display: "Not enough data for forecast. Need at least X months."

## 3. Forecasting Methods

### 3.1 Simple Historical Average

**Use when:** 3-11 months of data available, no clear trend.

**Method:**
```python
def forecast_simple_average(
    historical_transactions: List[Transaction],
    horizon_months: int = 3,
) -> List[ForecastPeriod]:
    """Project future based on average of historical periods."""
    
    # Group by month
    monthly_totals = group_by_month(historical_transactions)
    
    # Calculate average income and expense
    avg_income = mean([m.income for m in monthly_totals])
    avg_expense = mean([m.expense for m in monthly_totals])
    
    # Project future months
    forecasts = []
    for i in range(1, horizon_months + 1):
        future_date = today + relativedelta(months=i)
        forecasts.append(ForecastPeriod(
            date=future_date,
            income=avg_income,
            expense=avg_expense,
            balance=previous_balance + avg_income - avg_expense,
            method="simple_average",
            confidence="low" if len(monthly_totals) < 6 else "medium",
        ))
    
    return forecasts
```

**Pros:** Simple, explainable, stable.  
**Cons:** Ignores trends, seasonality.

### 3.2 Trend-Based Projection (Linear Regression)

**Use when:** 12+ months of data, visible trend.

**Method:**
```python
from scipy.stats import linregress

def forecast_trend_based(
    historical_transactions: List[Transaction],
    horizon_months: int = 6,
) -> List[ForecastPeriod]:
    """Project future using linear trend."""
    
    monthly_totals = group_by_month(historical_transactions)
    
    # Linear regression on expenses
    months = list(range(len(monthly_totals)))
    expenses = [m.expense for m in monthly_totals]
    
    slope, intercept, r_value, _, _ = linregress(months, expenses)
    
    # Project future
    forecasts = []
    last_month_index = len(monthly_totals)
    
    for i in range(1, horizon_months + 1):
        future_index = last_month_index + i
        projected_expense = Decimal(str(slope * future_index + intercept))
        
        # Similar for income
        projected_income = calculate_income_trend(monthly_totals, future_index)
        
        forecasts.append(ForecastPeriod(
            date=today + relativedelta(months=i),
            income=projected_income,
            expense=max(projected_expense, Decimal("0")),  # No negative
            method="linear_trend",
            confidence="medium" if r_value**2 > 0.5 else "low",
            r_squared=r_value**2,
        ))
    
    return forecasts
```

**Pros:** Captures growth/decline trends.  
**Cons:** Assumes linear continuation (rarely true forever).

### 3.3 Recurring Transaction Based

**Use when:** User has defined recurring templates.

**Method:**
```python
def forecast_recurring(
    recurring_templates: List[RecurringTemplate],
    horizon_months: int = 6,
) -> List[ForecastPeriod]:
    """Project based on known recurring transactions."""
    
    forecasts = []
    current_balance = get_current_balance()
    
    for i in range(1, horizon_months + 1):
        future_date = today + relativedelta(months=i)
        
        # Sum all recurring transactions for this month
        monthly_income = sum(
            t.amount for t in recurring_templates
            if t.transaction_type == "income" and is_active_in_month(t, future_date)
        )
        monthly_expense = sum(
            t.amount for t in recurring_templates
            if t.transaction_type == "expense" and is_active_in_month(t, future_date)
        )
        
        current_balance += monthly_income - monthly_expense
        
        forecasts.append(ForecastPeriod(
            date=future_date,
            income=monthly_income,
            expense=monthly_expense,
            balance=current_balance,
            method="recurring_templates",
            confidence="high",  # Known recurring
        ))
    
    return forecasts
```

**Pros:** Most accurate for predictable recurring.  
**Cons:** Misses discretionary spending.

### 3.4 Hybrid (Recurring + Historical Discretionary)

**Use when:** Recurring templates exist + historical data.

**Method:**
- Forecast recurring transactions exactly
- Add historical average of non-recurring (discretionary) spending
- Most realistic for typical users

```python
def forecast_hybrid(
    recurring_templates: List[RecurringTemplate],
    historical_transactions: List[Transaction],
    horizon_months: int = 6,
) -> List[ForecastPeriod]:
    """Combine known recurring with historical discretionary."""
    
    # Identify historical discretionary (non-recurring) spending
    discretionary = [
        t for t in historical_transactions
        if not matches_recurring_template(t, recurring_templates)
    ]
    
    avg_discretionary = mean_monthly_spending(discretionary)
    
    # Project each month
    forecasts = []
    for i in range(1, horizon_months + 1):
        future_date = today + relativedelta(months=i)
        
        recurring_income = sum_recurring_income(recurring_templates, future_date)
        recurring_expense = sum_recurring_expense(recurring_templates, future_date)
        
        total_expense = recurring_expense + avg_discretionary
        
        forecasts.append(ForecastPeriod(
            date=future_date,
            income=recurring_income,
            expense=total_expense,
            expense_recurring=recurring_expense,
            expense_discretionary=avg_discretionary,
            method="hybrid",
            confidence="medium",
        ))
    
    return forecasts
```

## 4. Scenario Planning

Allow users to adjust forecast assumptions:

### Scenario Types

**Baseline:**
- Current spending continues
- No adjustments

**Optimistic:**
- Expenses reduce by X%
- Income increases by Y%
- User-defined

**Pessimistic:**
- Expenses increase by X%
- Income decreases by Y%
- User-defined

**Custom:**
- User specifies:
  - Add/remove recurring transaction
  - One-time expense (car repair, vacation)
  - Income change (promotion, job loss)
  - Expense category change

### Implementation

```python
@dataclass
class ScenarioAdjustment:
    type: str  # "income_change", "expense_change", "add_recurring", "one_time"
    category_id: Optional[UUID]
    amount_change: Optional[Decimal]  # Percentage or absolute
    start_month: Optional[int]
    end_month: Optional[int]

def apply_scenario(
    baseline_forecast: List[ForecastPeriod],
    adjustments: List[ScenarioAdjustment],
) -> List[ForecastPeriod]:
    """Apply user adjustments to baseline forecast."""
    
    scenario_forecast = deepcopy(baseline_forecast)
    
    for period in scenario_forecast:
        for adj in adjustments:
            if adj.type == "expense_change":
                period.expense *= (1 + adj.amount_change / 100)
            elif adj.type == "income_change":
                period.income *= (1 + adj.amount_change / 100)
            elif adj.type == "one_time":
                if is_in_period(adj.start_month, period.date):
                    period.expense += adj.amount_change
            # ... handle other types
        
        # Recalculate balance
        period.balance = previous_balance + period.income - period.expense
    
    return scenario_forecast
```

## 5. Confidence Levels

**High:**
- Recurring templates with 6+ months history
- R² > 0.7 for trend-based

**Medium:**
- 6+ months historical average
- Recurring with 3-6 months history
- R² 0.5-0.7 for trend

**Low:**
- 3-5 months historical average
- Trend with R² < 0.5
- High variance in historical data

**Display:** "Confidence: Medium (based on 8 months of data)"

## 6. Presentation Requirements

### Visual Separation

- **Chart:** Historical data in solid line, forecast in dashed line
- **Color:** Historical = blue, forecast = orange
- **Shading:** Confidence interval around forecast (future enhancement)

### Methodology Disclosure

Display with every forecast:
```
Method: 6-month historical average
Period: Jan 2026 - Jun 2026
Assumptions:
  - Spending patterns remain consistent
  - No major life changes
  - Excludes one-time expenses
Confidence: Medium
```

### Disclaimers

> **Forecast Disclaimer**  
> This is a projection based on historical data and stated assumptions. Actual results may vary significantly. This is not financial advice.

## 7. Validation and Testing

### Backtesting

Test forecast accuracy on historical data:

```python
def backtest_forecast(
    historical_transactions: List[Transaction],
    method: str,
    train_months: int = 12,
    test_months: int = 3,
) -> BacktestResult:
    """Test forecast accuracy on historical data."""
    
    # Split data
    train_data = historical_transactions[:-test_months]
    test_data = historical_transactions[-test_months:]
    
    # Generate forecast using train data
    forecast = generate_forecast(train_data, method, horizon=test_months)
    
    # Compare to actual
    errors = []
    for i, period in enumerate(forecast):
        actual = test_data[i]
        error = abs(period.expense - actual.expense)
        errors.append(error)
    
    mae = mean(errors)  # Mean Absolute Error
    mape = mean(error / actual for error, actual in zip(errors, test_data))  # MAPE
    
    return BacktestResult(
        method=method,
        mae=mae,
        mape=mape,
        accuracy="good" if mape < 0.2 else "poor",
    )
```

### Test Cases

```python
# Test: Insufficient data
assert forecast_simple_average(transactions=2_months) raises InsufficientDataError

# Test: Zero division
assert forecast_trend_based(all_zero_expenses) returns zeros, not NaN

# Test: Negative projections
assert all(f.expense >= 0 for f in forecast)  # No negative expenses

# Test: Balance continuity
assert forecast[1].balance == forecast[0].balance + forecast[1].income - forecast[1].expense
```

## 8. Future Enhancements (Post-MVP)

- **ARIMA/SARIMA:** Seasonal patterns
- **Machine Learning:** XGBoost, Prophet for complex patterns
- **Monte Carlo:** Probabilistic forecasting with confidence intervals
- **External factors:** Holidays, economic indicators (with user consent)

## 9. Computational Requirements

- **Simple average:** O(n) where n = number of historical transactions
- **Trend-based:** O(n log n) for regression
- **Hybrid:** O(n + m) where m = recurring templates

Target: Forecast generation <2 seconds for 24 months of data.

## Next Steps

Create threat model document for security analysis.
