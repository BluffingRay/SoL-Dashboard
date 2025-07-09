import pandas as pd

def load_data(client):
    wb = client.open("School of Law Data")
    sheet1, sheet2, sheet3 = wb.sheet1, wb.get_worksheet(1), wb.get_worksheet(2)

    df_enroll = pd.DataFrame(sheet1.get_all_records())
    df_grad = pd.DataFrame(sheet2.get_all_records())
    df_cohort = pd.DataFrame(sheet3.get_all_records())

    return df_enroll, df_grad, df_cohort
