import json
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from foundation import llm
from parser.gz_parse import parse_deal, parse_deal_lots, parse_deal_docs, parse_doc


def split_text(text: str, chunk_size: int = 6000) -> list[str]:
    """Разбивает текст на части по абзацам, не обрывая посередине."""
    paragraphs = text.split('\n')
    chunks = []
    current = []
    current_len = 0

    for para in paragraphs:
        if current_len + len(para) > chunk_size and current:
            chunks.append('\n'.join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += len(para)

    if current:
        chunks.append('\n'.join(current))

    return chunks


@tool
async def get_deal_info(url: str) -> str:
    """
    Получает общие сведения о госзакупке.
    Вызывай первым при анализе любой госзакупки.
    :param url: ссылка на объявление госзакупки
    """
    deal_info = await parse_deal(url)
    return deal_info
    # return json.dumps(deal_info, ensure_ascii=False, indent=2)


@tool
async def get_deal_lots(url: str) -> str:
    """
    Получает сведения о лотах госзакупки.
    Вызывай после get_deal_info.
    :param url: ссылка на объявление госзакупки
    """
    lots_info = await parse_deal_lots(url)
    return json.dumps(lots_info, ensure_ascii=False, indent=2)


@tool
async def get_deal_docs_info(url: str) -> str:
    """
    Читает текст и таблицы из технической документации госзакупки.
    Поддерживает PDF, DOC, DOCX, XLS, XLSX, ZIP, RAR.
    Если в результате есть сообщение об изображениях — вызови get_deal_docs_images.
    :param url: ссылка на объявление госзакупки
    """

    docs = await parse_deal_docs(url)
    parts = []
    has_images = False

    for file_name, file_data in docs.items():
        obj_doc = await parse_doc(file_name, file_data)

        if isinstance(obj_doc, str):
            parts.append(f"[{file_name}]\n{obj_doc}")
            continue

        doc_list = obj_doc if isinstance(obj_doc, list) else [obj_doc]

        for doc in doc_list:
            if isinstance(doc, str):
                parts.append(f"[{file_name}]\n{doc}")
                continue

            section = [f"=== {file_name} ==="]

            if doc.text:
                text = doc.text.strip()
                chunks = split_text(text, chunk_size=6000)

                if len(chunks) == 1:
                    # Короткий документ — отправляем целиком
                    section.append(f"ТЕКСТ:\n{chunks[0]}")
                else:
                    # Длинный документ — суммаризируем каждый чанк через LLM
                    summaries = []
                    for i, chunk in enumerate(chunks):
                        prompt = (
                            f"Это часть {i+1}/{len(chunks)} документа '{file_name}' "
                            f"из технической документации госзакупки Казахстана.\n"
                            f"Извлеки ключевую информацию: требования, характеристики, "
                            f"сроки, суммы, условия. Отвечай на русском кратко.\n\n{chunk}"
                        )
                        resp = await llm.ainvoke(prompt)
                        summaries.append(f"[Часть {i+1}]\n{resp.content}")

                    section.append("ТЕКСТ (суммаризирован):\n" + "\n\n".join(summaries))

            if doc.tables:
                for i, table in enumerate(doc.tables):
                    rows = [" | ".join(str(cell) for cell in row) for row in table]
                    section.append(f"ТАБЛИЦА {i + 1}:\n" + "\n".join(rows))

            if doc.images_b64:
                has_images = True
                section.append(f"[{len(doc.images_b64)} изображений/сканов]")

            parts.append("\n".join(section))

    result = "\n\n".join(parts)

    if has_images:
        result += (
            "\n\n[Документы содержат сканы/изображения. "
            "Вызови get_deal_docs_images(url) для их анализа.]"
        )

    return result or "[Документы не содержат читаемого текста]"


@tool
async def get_deal_docs_images(url: str) -> str:
    """
    Анализирует сканы и картинки из документов через vision модель.
    Вызывай только если get_deal_docs_info сообщил о наличии изображений.
    :param url: ссылка на объявление госзакупки
    """
    docs = await parse_deal_docs(url)
    results = []

    for file_name, file_data in docs.items():
        obj_doc = await parse_doc(file_name, file_data)

        if isinstance(obj_doc, str):
            continue

        doc_list = obj_doc if isinstance(obj_doc, list) else [obj_doc]

        for doc in doc_list:
            if isinstance(doc, str) or not doc.images_b64:
                continue

            # Обрабатываем все картинки батчами по 3
            all_results = []
            batch_size = 3
            images = doc.images_b64

            for i in range(0, len(images), batch_size):
                batch = images[i:i + batch_size]
                content = [
                    {
                        "type": "text",
                        "text": (
                            f"Документ: {file_name}, страницы {i+1}-{i+len(batch)}. "
                            "Извлеки весь текст, таблицы и технические требования. "
                            "Это техдокументация госзакупки Казахстана. "
                            "Отвечай на русском языке."
                        )
                    },
                    *[
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                        }
                        for b64 in batch
                    ]
                ]
                response = await llm.ainvoke([HumanMessage(content=content)])
                all_results.append(response.content)

            results.append(f"=== {file_name} (сканы) ===\n" + "\n\n".join(all_results))

    return "\n\n".join(results) or "[Изображений в документах не найдено]"


agent_tools = [get_deal_info, get_deal_lots, get_deal_docs_info, get_deal_docs_images]
