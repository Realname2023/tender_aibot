import re
from urllib.parse import urlparse, parse_qs, urlencode


def get_page_url(base_url: str, page: int) -> str:
    """Подставляет номер страницы в уже сконвертированный URL."""
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query)
    params['page'] = [str(page)]
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode({k: v[0] for k, v in params.items()})}"

def convert_search_url(url: str, count_record: int = 10, page: int = 1) -> str | None:
    """
    Конвертирует URL поиска госзакупок в короткий формат.
    Возвращает None если URL невалидный или неконвертируемый.
    """
    try:
        parsed = urlparse(url)

        # Проверка что это именно ссылка поиска ГЗ
        if not (parsed.scheme == 'https' and
                parsed.netloc == 'goszakup.gov.kz' and
                parsed.path == '/ru/search/announce'):
            return None

        params = parse_qs(parsed.query, keep_blank_values=False)

        new_params = {}
        for key, values in params.items():
            values = [v for v in values if v.strip()]
            if not values:
                continue
            if len(values) == 1:
                clean_key = key.replace('[]', '')
                new_params[clean_key] = values[0]
            else:
                base_key = key.replace('[]', '')
                for i, v in enumerate(values):
                    new_params[f"{base_key}[{i}]"] = v

        new_params['count_record'] = str(count_record)
        new_params['page'] = str(page)

        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(new_params)}"

    except Exception:
        return None

def extract_gz_url(text: str) -> str | None:
    """Извлекает ссылку поиска ГЗ из текста через re."""
    pattern = r'https://goszakup\.gov\.kz/ru/search/announce[^\s]*'
    match = re.search(pattern, text)
    return match.group(0) if match else None
