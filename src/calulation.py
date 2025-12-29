import pandas as pd
import io

async def unwrap_value(x):
    if isinstance(x, dict):
        return x.get("value")
    return x

async def safe_divide(numerator, denominator):
    numerator = await unwrap_value(numerator)
    denominator = await unwrap_value(denominator)
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator

async def calculate_esrs_indicators(data):
    def get_item(key):
        item = data.get(key)
        if isinstance(item, dict):
            return item
        return {"value": None, "unit": None, "page": None, "confidence": None, "source_section": None, "notes": None}

    scope1_item = get_item("Scope1_Emissions")
    scope2_item = get_item("Scope2_Emissions")
    scope3_item = get_item("Scope3_Emissions")
    revenue_item = get_item("Revenue_EUR")
    total_energy_item = get_item("Total_Energy")
    renewable_item = get_item("Renewable_Energy")
    net_zero_item = get_item("NetZero_Target_Year")
    green_fin_item = get_item("Green_Financing_Volume")
    total_emp_item = get_item("Total_Employees")
    female_emp_item = get_item("Female_Employees")
    male_salary_item = get_item("Avg_Salary_Male")
    female_salary_item = get_item("Avg_Salary_Female")
    training_item = get_item("Total_Training_Hours")
    emp_left_item = get_item("Employees_Left")
    avg_emp_item = get_item("Average_Employees")
    work_acc_item = get_item("Work_Accidents")
    cba_item = get_item("Employees_CBA_Covered")
    female_board_item = get_item("Female_Board_Members")
    total_board_item = get_item("Total_Board_Members")
    board_meet_item = get_item("Board_Meetings")
    corruption_item = get_item("Corruption_Incidents")
    trade_payables_item = get_item("Trade_Payables")
    purchases_item = get_item("Purchases_From_Suppliers")
    suppliers_screened_item = get_item("Suppliers_Screened_ESG")
    total_suppliers_item = get_item("Total_Suppliers")


    scope_values = [v for v in [scope1_item["value"], scope2_item["value"], scope3_item["value"]] if isinstance(v, (int, float))]
    total_ghg = sum(scope_values) if scope_values else None
    ghg_intensity = await safe_divide(total_ghg, revenue_item)
    renewable_pct = await safe_divide(renewable_item, total_energy_item)
    if renewable_pct is not None:
        renewable_pct *= 100
    female_pct = await safe_divide(female_emp_item, total_emp_item)
    if female_pct is not None:
        female_pct *= 100
    gender_pay_gap = await safe_divide(male_salary_item["value"] - female_salary_item["value"], male_salary_item)
    if gender_pay_gap is not None:
        gender_pay_gap *= 100
    training_per_emp = await safe_divide(training_item, total_emp_item)
    employee_turnover = await safe_divide(emp_left_item, avg_emp_item)
    if employee_turnover is not None:
        employee_turnover *= 100
    cba_pct = await safe_divide(cba_item, total_emp_item)
    if cba_pct is not None:
        cba_pct *= 100
    board_female_pct = await safe_divide(female_board_item, total_board_item)
    if board_female_pct is not None:
        board_female_pct *= 100
    avg_payment_period = await safe_divide(trade_payables_item, purchases_item)
    if avg_payment_period is not None:
        avg_payment_period *= 365
    suppliers_esg_pct = await safe_divide(suppliers_screened_item, total_suppliers_item)
    if suppliers_esg_pct is not None:
        suppliers_esg_pct *= 100

    esrs = {
        # Environmental (E1)
        "Scope1_Emissions": {**scope1_item, "indicator_name": "Total Scope 1 GHG Emissions", "value": scope1_item["value"]},
        "Scope2_Emissions": {**scope2_item, "indicator_name": "Total Scope 2 GHG Emissions", "value": scope2_item["value"]},
        "Scope3_Emissions": {**scope3_item, "indicator_name": "Total Scope 3 GHG Emissions", "value": scope3_item["value"]},
        "GHG_Emissions_Intensity": {**revenue_item, "indicator_name": "GHG Emissions Intensity", "value": ghg_intensity, "unit": "tCO2e per €M revenue"},
        "Total_Energy": {**total_energy_item, "indicator_name": "Total Energy Consumption", "value": total_energy_item["value"]},
        "Renewable_Energy_Percentage": {**renewable_item, "indicator_name": "Renewable Energy Percentage", "value": renewable_pct, "unit": "%"},
        "NetZero_Target_Year": {**net_zero_item, "indicator_name": "Net Zero Target Year", "value": net_zero_item["value"]},
        "Green_Financing_Volume": {**green_fin_item, "indicator_name": "Green Financing Volume", "value": green_fin_item["value"]},

        # Social (S1)
        "Total_Employees": {**total_emp_item, "indicator_name": "Total Employees", "value": total_emp_item["value"]},
        "Female_Employees_Percentage": {**female_emp_item, "indicator_name": "Female Employees %", "value": female_pct, "unit": "%"},
        "Gender_Pay_Gap": {**female_salary_item, "indicator_name": "Gender Pay Gap %", "value": gender_pay_gap, "unit": "%"},
        "Training_Hours_Per_Employee": {**training_item, "indicator_name": "Training Hours per Employee", "value": training_per_emp},
        "Employee_Turnover_Rate": {**emp_left_item, "indicator_name": "Employee Turnover Rate %", "value": employee_turnover, "unit": "%"},
        "Work_Accidents": {**work_acc_item, "indicator_name": "Work-Related Accidents", "value": work_acc_item["value"]},
        "Employees_CBA_Covered": {**cba_item, "indicator_name": "Collective Bargaining Coverage %", "value": cba_pct, "unit": "%"},
        
        # Governance (G1/G2)
        "Board_Female_Representation": {**female_board_item, "indicator_name": "Board Female Representation %", "value": board_female_pct, "unit": "%"},
        "Board_Meetings": {**board_meet_item, "indicator_name": "Board Meetings", "value": board_meet_item["value"]},
        "Corruption_Incidents": {**corruption_item, "indicator_name": "Corruption Incidents", "value": corruption_item["value"]},
        "Avg_Payment_Period_To_Suppliers": {**trade_payables_item, "indicator_name": "Avg Payment Period to Suppliers", "value": avg_payment_period, "unit": "days"},
        "Suppliers_Screened_ESG_Percentage": {**suppliers_screened_item, "indicator_name": "Suppliers Screened for ESG %", "value": suppliers_esg_pct, "unit": "%"},
    }

    return esrs



def esrs_to_csv(esrs_dict):

    ESRS_ORDER = [
        "Scope1_Emissions",
        "Scope2_Emissions",
        "Scope3_Emissions",
        "GHG_Emissions_Intensity",
        "Total_Energy",
        "Renewable_Energy_Percentage",
        "NetZero_Target_Year",
        "Green_Financing_Volume",

        "Total_Employees",
        "Female_Employees_Percentage",
        "Gender_Pay_Gap",
        "Training_Hours_Per_Employee",
        "Employee_Turnover_Rate",
        "Work_Accidents",
        "Employees_CBA_Covered",

        "Board_Female_Representation",
        "Board_Meetings",
        "Corruption_Incidents",
        "Avg_Payment_Period_To_Suppliers",
        "Suppliers_Screened_ESG_Percentage",
    ]

    rows = []

    for key in ESRS_ORDER:
        item = esrs_dict.get(key, {})

        rows.append({
            "indicator_code": key,
            "indicator_name": item.get("indicator_name"),
            "value": item.get("value"),
            "unit": item.get("unit"),
            "confidence": item.get("confidence"),
            "source_page": item.get("page"),  
            "source_section": item.get("source_section"),
            "notes": item.get("notes"),
        })

    df = pd.DataFrame(rows)

    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)

    return buf.getvalue()