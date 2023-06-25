from io import StringIO
import re
import os
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from wrapt_timeout_decorator import timeout
from logging import getLogger

_threshold_intersection = 0.3  # if the intersection is large enough.

logger = getLogger()


def normalize_spaces(text: str) -> str:
    """Removes single line breaks to highlight paragraphs correctly"""
    return re.sub("[ ]{1,}", " ",
                  re.sub("(?<!\n)\n(?!\n){1,}", " ",
                         text)).strip()


@timeout(2, use_signals=False)
def read_pdf_page(page, codec: str):
    """Read pdf page"""
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    interpreter.process_page(page)
    return retstr.getvalue()


@timeout(120, use_signals=False)
def convert_pdf_to_txt(path: str, codec: str = "utf-8"):
    with open(path, "rb") as fp:
        pages = PDFPage.get_pages(fp,
                                  set(),
                                  maxpages=0,
                                  password="",
                                  caching=True,
                                  check_extractable=True)
        parsed_result = {}

        for page_num, page in enumerate(pages):
            try:
                text = normalize_spaces(read_pdf_page(page, codec))

                parsed_result[page_num] = {"text": text}
                if text.startswith("Графическая часть"):
                    # пропускаем картинки
                    logger.warning(f'Skip image page {page_num} from {path}')
                    break
            except Exception as ex:
                # пропускаем кривые страницы с изображениями
                logger.error(
                    f'Skip image page {page_num} from {path} becouse {str(ex)}')
                parsed_result[page_num] = {"text": ''}

    return parsed_result


# название документа:список словарей(номер страницы:текст)
def parse_pdf_bucket(folder: str, update_state) -> dict[str, list[dict[str, str]]]:
    documents = {}
    files = os.listdir(folder)
    progres = 0
    for fn in files:
        print('FILE:', fn)
        filename = os.path.join(folder, fn)
        try:
            res = convert_pdf_to_txt(filename)
            documents[fn] = res
        except Exception as ex:
            logger.error(
                f'Error while document {filename} processing {str(ex)}')
            documents[fn] = 'long time parsing'
        progres += 1
        update_state(state='PROGRESS', meta={
                     'done': progres, 'total': len(files)})
    return documents


# documents = parse_pdf_bucket(folder='drive/MyDrive/jetfork_2023_dataset/doc1')
