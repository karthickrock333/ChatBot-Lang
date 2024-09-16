def few_shots():
    fs =[
    {'Question': "Can you provide the first and last names of all providers who are listed as Orthopedic specialists?",
     'SQLQuery': "SELECT PROVIDERFIRSTNAME, PROVIDERLASTNAME FROM provider WHERE SPECIALTY = 'Orthopedic' limit 1;",
     'SQLResult': "Result of the SQL query",
     'Answer': "0"},

    {'Question': "What is the provider type for the provider named 'Makayla Ellis'?",
     'SQLQuery': "SELECT PROVIDERTYPE FROM provider WHERE PROVIDERFIRSTNAME = 'Makayla' AND PROVIDERLASTNAME = 'Ellis';",
     'SQLResult': "Result of the SQL query",
     'Answer': "DO"},

    {'Question': "Could you provide me with the patient IDs for all clinical encounters where the encounter type is 'CL'?",
    'SQLQuery': "select PATIENTID FROM CILINCALENCOUNTER WHERE CLINICALENCOUNTERTYPE='CL'",
    'SQLResult': "Result of the SQL query",
    'Answer': " "},

    {  'Question': "Can you provide the patient IDs for clinical encounters where the encounter type is 'CL' and the parent context ID is 2001?",
        'SQLQuery': "select PATIENTID FROM CILINCALENCOUNTER WHERE CLINICALENCOUNTERTYPE='CL' AND CONTEXTPARENTCONTEXTID = 2001",
        'SQLResult': "Result of the SQL query",
        'Answer': " "},

    {'Question': "What is the patient's email address and their primary provider's last name?",
     'SQLQuery': "SELECT p.EMAIL, prv.PROVIDERLASTNAME FROM patient p JOIN provider prv ON p.PRIMARYPROVIDERID = prv.PROVIDERID limit 1;",
     'SQLResult': "Result of the SQL query",
     'Answer': " "},

     {'Question': "give me patient details of this patientid 361",
      'SQLQuery': "SELECT PROVIDERFIRSTNAME, PROVIDERLASTNAME FROM provider WHERE SPECIALTY = 'Orthopedic' limit 1;",
      'SQLResult': "Result of the SQL query",
      'Answer': "0"},
]
    return fs
