import re
from bs4 import BeautifulSoup as BS
from foundation import parse_gz_deals, parse_bytes
from parser.read_files import extract_document


async def parse_deal(linc_deal: str) -> str:
    soup = await parse_gz_deals(linc_deal)
    if isinstance(soup, BS):
        main_labels = soup.find_all('label', {'class': 'col-sm-4 control-label'})
        main_values = soup.find_all('input', {'class':"form-control"})
        heads = [head.text.strip() for head in main_labels]
        values = [val.get('value') for val in main_values]
        main_data = '\n'.join(f"{head}: {val}" for head, val in zip(heads, values) )
        sec_tables = soup.find_all('table', {'class':"table table-bordered table-hover table-striped"})
        sec_heads = []
        sec_values = []
        for obj in sec_tables:
            sec_heads.extend(obj.find_all('th'))
            sec_values.extend(obj.find_all('td'))
        sec_heads_texts = [val.text.strip() for val in sec_heads]
        sec_values_texts = [vals.text.strip() for vals in sec_values]
        sec_data = '\n'.join(f'{head}: {val}' for head, val in zip(sec_heads_texts, sec_values_texts))

        notifications = soup.find('div', {'class': 'alert alert-success'})
        if notifications is not None:
            paragrafs = notifications.find_all('p')
            txts = ''
            lincs = notifications.find_all('a')
            for par in paragrafs:
                txt = par.text.strip()
                txts += txt
            if lincs != []:
                for linc in lincs:
                    ltxt = linc.text.strip()
                    lhref = linc.get('href')
                    lincs_data = f'{ltxt}: {lhref}\n'
                    txts += lincs_data

            sec_data = f'{sec_data}\nкомменты: {txts}'

        deal_data = f'{main_data}\n{sec_data}'

        return deal_data
    else:
        return soup


async def parse_deal_lots(linc_deal: str) -> list:
    lots_url = f'{linc_deal}?tab=lots'
    soup = await parse_gz_deals(lots_url)
    if isinstance(soup, BS):
        lots = []
        table_of_lots = soup.find('table', {'class':"table table-bordered table-hover table-striped"})
        table_heads = table_of_lots.find_all('th')
        heads = [head.text.strip() for head in table_heads]
        rows = table_of_lots.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            values = [col.text.strip() for col in cols]
            if values != []:
                lots.append(dict(zip(heads, values)))
        return lots
    else:
        return soup



async def parse_deal_docs(linc_deal: str) -> dict:
    data_docs = {}
    linc_deal_docs = f'{linc_deal}?tab=documents'
    # url = None
    soup = await parse_gz_deals(linc_deal_docs)
    if isinstance(soup, BS):
        row = soup.find_all("button", {'class': 'btn btn-primary btn-sm'})
        for i in row:
            url_data = i.get('onclick')
            doc_tr = i.find_parent('tr')
            doc_text = doc_tr.find('td').text.strip()
            if 'Техн' in doc_text or 'Квалификац' in doc_text:
                match = re.search(r'actionModalShowFiles\((\d+),(\d+)\)', url_data)
                if match:
                    result = f"/{match.group(1)}/{match.group(2)}"
                    url = f'https://goszakup.gov.kz/ru/announce/actionAjaxModalShowFiles{result}'
                    soup2 = await parse_gz_deals(url)
                    if isinstance(soup2, BS):
                        linc_docs = soup2.find_all('a')
                        c = 0
                        for i in linc_docs:
                            data_doc = i.get('href')
                            if 'v3bl' in data_doc:
                                txt = i.get_text()
                                doc_txt = f'{str(c)}{txt}'
                                data_docs.update({doc_txt: data_doc})
                                c += 1
                    else:
                        return soup2
        return data_docs
    else:
        return soup

async def parse_doc(txt: str, data_doc: str):
    file_bytes = await parse_bytes(data_doc)

    if not file_bytes or isinstance(file_bytes, str):
        msg = f'Ошибка не удалось прочитать файл {txt} {data_doc}'
        print(msg)
        return msg

    results = extract_document(txt, file_bytes, lang='ru')
    return results
