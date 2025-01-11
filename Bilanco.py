import requests
from bs4 import BeautifulSoup
import pandas as pd

hisseler=["EREGL","TAVHL"]  #Hisse kodlarını istediğiniz sayıda yazabilirsiniz

for i in hisseler:
    hisse=i
    tarihler=[]
    yıllar=[]
    donemler=[]
    grup=[]

    url1="https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/sirket-karti.aspx?hisse="+hisse
    r1=requests.get(url1)
    soup=BeautifulSoup(r1.text,"html.parser")
    secim=soup.find("select",id="ddlMaliTabloFirst")
    secim2=soup.find("select",id="ddlMaliTabloGroup")
    
    try:
        cocuklar=secim.findChildren("option")
        grup=secim2.find("option")["value"]
        
        for i in cocuklar:
            tarihler.append(i.string.rsplit("/"))
        for j in tarihler:
            yıllar.append(j[0])
            donemler.append(j[1])

        if len(tarihler)>=4:
            parametreler=(
                ("companyCode",hisse),
                ("exchange","TRY"), #Eğer dolar bazlı istiyorsanız "TRY" yerine "USD" yazınız
                ("financialGroup",grup),
                ("year1",yıllar[0]),
                ("period1",donemler[0]),
                ("year2",yıllar[1]),
                ("period2",donemler[1]),
                ("year3",yıllar[2]),
                ("period3",donemler[2]),
                ("year4",yıllar[3]),
                ("period4",donemler[3]))
            url2="https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/MaliTablo"
            r2=requests.get(url2,params=parametreler).json()["value"]
            veri=pd.DataFrame.from_dict(r2)
            veri.drop(columns=["itemCode","itemDescEng"],inplace=True)           
        else:
            continue
    except AttributeError:
        continue
    
    del tarihler[0:4]
    tumveri=[veri]
        
    for _ in range(0,12):
        if len(tarihler)==len(yıllar):
            del tarihler[0:4]
        else:
            yıllar=[]
            donemler=[]
            for j in tarihler:
                yıllar.append(j[0])
                donemler.append(j[1])
            
            if len(tarihler)>=4:
                parametreler2=(
                ("companyCode",hisse),
                ("exchange","TRY"), #Eğer dolar bazlı istiyorsanız "TRY" yerine "USD" yazınız
                ("financialGroup",grup),
                ("year1",yıllar[0]),
                ("period1",donemler[0]),
                ("year2",yıllar[1]),
                ("period2",donemler[1]),
                ("year3",yıllar[2]),
                ("period3",donemler[2]),
                ("year4",yıllar[3]),
                ("period4",donemler[3]))
                r3=requests.get(url2,params=parametreler2).json()["value"]
                veri2=pd.DataFrame.from_dict(r3)
                try:
                    veri2.drop(columns=["itemCode","itemDescTr","itemDescEng"],inplace=True)
                    tumveri.append(veri2)
                except KeyError:
                    continue
    veri3=pd.concat(tumveri,axis=1)
    baslık=["Bilanço"]
    for i in cocuklar:
        baslık.append(i.string)

    baslıkfark=len(baslık)-len(veri3.columns)

    if baslıkfark!=0:
        del baslık[-baslıkfark:]

    veri3=veri3.set_axis(baslık,axis=1)
    veri3[baslık[1:]]=veri3[baslık[1:]].astype(float)
    veri3=veri3.fillna(0)
    dizin="C:/Users/YUNUS/Desktop" #Dosyayı kaydetmek istediğiniz dizini yazın
    veri3.to_excel(dizin+"/{}.xlsx".format(hisse),index=False)