FUNDAMENTAL_RAG_SPEC = {

    "Scope1_Emissions": {
        "indicator_name": "Scope 1 GHG Emissions",
        "units": ["tCO2e", "ktCO2e", "MtCO2e"],
        "question": "What is the reported total Scope 1 greenhouse gas emissions?",
        "alt_questions": [
            "What is the company's Scope 1 GHG emissions?",
            "How many tonnes of CO2e are emitted under Scope 1?",
            "Report the Scope 1 emissions value."
        ]
    },

    "Scope2_Emissions": {
        "indicator_name": "Scope 2 GHG Emissions",
        "units": ["tCO2e", "ktCO2e", "MtCO2e"],
        "question": "What is the reported total Scope 2 greenhouse gas emissions?",
        "alt_questions": [
            "What is the company’s Scope 2 GHG emissions?",
            "How many tonnes of CO2e are emitted under Scope 2?",
            "Report the Scope 2 emissions value."
        ]
    },

    "Scope3_Emissions": {
        "indicator_name": "Scope 3 GHG Emissions",
        "units": ["tCO2e", "ktCO2e", "MtCO2e"],
        "question": "What is the reported total Scope 3 greenhouse gas emissions?",
        "alt_questions": [
            "What is the company’s Scope 3 GHG emissions?",
            "How many tonnes of CO2e are emitted under Scope 3?",
            "Report the Scope 3 emissions value."
        ]
    },

    "Revenue_EUR": {
        "indicator_name": "Company Revenue",
        "units": ["EUR", "EUR million", "EUR billion"],
        "question": "What is the company’s total revenue?",
        "alt_questions": [
            "What is the company’s total turnover?",
            "What is the organisation’s total revenue for the reporting year?",
            "State the reported revenue amount."
        ]
    },

    "Total_Energy": {
        "indicator_name": "Total Energy Consumption",
        "units": ["MWh", "GWh", "GJ", "TJ"],
        "question": "What is the total energy consumption reported?",
        "alt_questions": [
            "How much total energy did the company consume?",
            "Report the total energy consumption value.",
            "What is the organisation’s total energy use?"
        ]
    },

    "Renewable_Energy": {
        "indicator_name": "Renewable Energy Consumption",
        "units": ["MWh", "GWh", "GJ", "TJ"],
        "question": "How much renewable energy was consumed?",
        "alt_questions": [
            "What is the renewable energy consumption?",
            "Report the amount of renewable energy used.",
            "How much of the company’s energy came from renewable sources?"
        ]
    },

    "NetZero_Target_Year": {
        "indicator_name": "Net Zero Target Year",
        "units": ["year"],
        "question": "What is the company’s stated net-zero target year?",
        "alt_questions": [
            "When does the company plan to achieve net zero?",
            "What is the announced carbon neutrality target year?",
            "State the organisation’s net-zero commitment year."
        ]
    },

    "Green_Financing_Volume": {
        "indicator_name": "Green Financing Volume",
        "units": ["EUR", "EUR million", "EUR billion"],
        "question": "What is the total value of green or sustainability-linked financing?",
        "alt_questions": [
            "How much green financing did the company raise?",
            "Report the sustainability-linked financing volume.",
            "What is the value of green bonds or green loans?"
        ]
    },



    "Total_Employees": {
        "indicator_name": "Total Employees (FTE)",
        "units": ["FTE", "headcount", "employees"],
        "question": "What is the total number of employees (FTE)?",
        "alt_questions": [
            "What is the total workforce size?",
            "How many employees does the company employ?",
            "Report the total number of FTE employees."
        ]
    },

    "Female_Employees": {
        "indicator_name": "Number of Female Employees",
        "units": ["FTE", "headcount", "employees"],
        "question": "How many female employees are there?",
        "alt_questions": [
            "What is the number of women employed by the company?",
            "Report the female employee headcount.",
            "How many female FTE employees are reported?"
        ]
    },

    "Avg_Salary_Male": {
        "indicator_name": "Average Male Salary",
        "units": ["EUR/year", "EUR/month", "EUR/hour"],
        "question": "What is the average salary of male employees?",
        "alt_questions": [
            "Report the average male employee salary.",
            "What is the mean salary for male workers?",
            "What is the male compensation level?"
        ]
    },

    "Avg_Salary_Female": {
        "indicator_name": "Average Female Salary",
        "units": ["EUR/year", "EUR/month", "EUR/hour"],
        "question": "What is the average salary of female employees?",
        "alt_questions": [
            "Report the average female employee salary.",
            "What is the mean salary for female workers?",
            "What is the female compensation level?"
        ]
    },

    "Total_Training_Hours": {
        "indicator_name": "Total Employee Training Hours",
        "units": ["hours"],
        "question": "What is the total number of employee training hours?",
        "alt_questions": [
            "How many hours of employee training were delivered?",
            "Report total workforce training hours.",
            "What is the total volume of training hours?"
        ]
    },

    "Employees_Left": {
        "indicator_name": "Employees Who Left During Year",
        "units": ["employees", "headcount"],
        "question": "How many employees left the company during the year?",
        "alt_questions": [
            "What is the number of employee exits?",
            "How many employees resigned or left?",
            "Report the count of employees who left."
        ]
    },

    "Average_Employees": {
        "indicator_name": "Average Number of Employees",
        "units": ["employees", "FTE"],
        "question": "What is the average number of employees during the reporting year?",
        "alt_questions": [
            "Report the average workforce size.",
            "What is the mean employee count?",
            "What is the average FTE value?"
        ]
    },

    "Work_Accidents": {
        "indicator_name": "Work-Related Accidents",
        "units": ["count", "cases", "incidents"],
        "question": "How many work-related accidents were reported?",
        "alt_questions": [
            "What is the number of occupational accidents?",
            "Report the total accident incidents.",
            "How many workplace injuries occurred?"
        ]
    },

    "Employees_CBA_Covered": {
        "indicator_name": "Employees Covered by Collective Bargaining",
        "units": ["employees", "FTE"],
        "question": "How many employees are covered by collective bargaining agreements?",
        "alt_questions": [
            "What number of employees are under collective agreements?",
            "Report the employees covered by CBAs.",
            "How many workers are union or CBA covered?"
        ]
    },


 
    "Female_Board_Members": {
        "indicator_name": "Female Board Members",
        "units": ["count"],
        "question": "How many female board members are there?",
        "alt_questions": [
            "Report the number of women on the board.",
            "What is the female board representation count?",
            "How many female directors serve on the board?"
        ]
    },

    "Total_Board_Members": {
        "indicator_name": "Total Board Members",
        "units": ["count"],
        "question": "What is the total number of board members?",
        "alt_questions": [
            "Report the size of the board of directors.",
            "How many directors are on the board?",
            "What is the total board headcount?"
        ]
    },

    "Board_Meetings": {
        "indicator_name": "Board Meetings Held",
        "units": ["count/year"],
        "question": "How many board meetings were held during the year?",
        "alt_questions": [
            "Report the number of board meetings conducted.",
            "How many times did the board meet?",
            "What is the annual count of board meetings?"
        ]
    },

    "Corruption_Incidents": {
        "indicator_name": "Corruption Incidents",
        "units": ["count", "cases"],
        "question": "How many confirmed corruption incidents were reported?",
        "alt_questions": [
            "Report the number of bribery or corruption violations.",
            "How many integrity incidents were recorded?",
            "What is the count of corruption cases?"
        ]
    },

    "Trade_Payables": {
        "indicator_name": "Trade Payables",
        "units": ["EUR", "EUR million", "EUR billion"],
        "question": "What is the total value of trade payables?",
        "alt_questions": [
            "Report the balance of trade payables.",
            "What is the amount owed to suppliers?",
            "State the reported trade payable value."
        ]
    },

    "Purchases_From_Suppliers": {
        "indicator_name": "Purchases from Suppliers",
        "units": ["EUR", "EUR million", "EUR billion"],
        "question": "What is the total value of purchases from suppliers?",
        "alt_questions": [
            "Report the procurement or purchasing spend.",
            "How much was spent on suppliers?",
            "What is the total supplier purchase value?"
        ]
    },

    "Suppliers_Screened_ESG": {
        "indicator_name": "Suppliers Screened for ESG",
        "units": ["count"],
        "question": "How many suppliers were screened for ESG or sustainability?",
        "alt_questions": [
            "Report the number of suppliers assessed for ESG risk.",
            "How many suppliers underwent ESG evaluation?",
            "What is the ESG-screened supplier count?"
        ]
    },

    "Total_Suppliers": {
        "indicator_name": "Total Suppliers",
        "units": ["count"],
        "question": "What is the total number of suppliers?",
        "alt_questions": [
            "Report the total supplier base size.",
            "How many suppliers does the company have?",
            "What is the supplier headcount?"
        ]
    }
}
