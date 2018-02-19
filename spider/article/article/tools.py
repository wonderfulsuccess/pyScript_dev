def remove_csv_noise(uncerten_str):
    certen_str = str(uncerten_str).replace(',','，').replace('\n','').replace('\r','')
    return certen_str
