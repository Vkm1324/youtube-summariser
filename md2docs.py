import markdown
from bs4 import BeautifulSoup

def markdown_to_document_structure(mdstring):
    html = markdown.markdown(mdstring, extensions=['fenced_code', 'tables'])
    soup = BeautifulSoup(html, "html.parser")
    
    doc_structure = []
    for element in soup.recursiveChildGenerator():
        if element.name:
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                doc_structure.append({
                    "type": "heading",
                    "level": int(element.name[1]),
                    "text": element.get_text(strip=True)
                })
            elif element.name == "p":
                doc_structure.append({
                    "type": "paragraph",
                    "text": element.get_text(strip=True)
                })
            elif element.name == "ul":
                items = [li.get_text(strip=True) for li in element.find_all("li")]
                doc_structure.append({
                    "type": "list",
                    "items": items
                })
            elif element.name == "pre":
                code = element.get_text()
                lang = element.code.get("class", [""])[0].replace("language-", "") if element.code else ""
                doc_structure.append({
                    "type": "code",
                    "language": lang,
                    "code": code.strip()
                })
    return doc_structure
