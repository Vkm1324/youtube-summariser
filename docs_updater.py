import os
import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import DOCUMENT_ID, SERVICE_ACCOUNT_KEY_FILE
from md2docs import markdown_to_document_structure
# OAuth scopes required for Docs API (for editing/creating documents)
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file' # Needed if you also create docs
]

def authenticate_docs_api():
    """Authenticates with Google Docs API using a service account."""
    try:
        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_KEY_FILE, scopes=SCOPES
        )
        service = build('docs', 'v1', credentials=credentials)
        print("Successfully authenticated with Google Docs API.")
        return service
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None

def get_document_length(service, document_id):
    """Returns a safe insertion index just before the end of the document."""
    try:
        doc = service.documents().get(documentId=document_id, fields='body.content').execute()
        content = doc.get('body', {}).get('content', [])
        
        # Find the last element with a valid 'endIndex'
        for element in reversed(content):
            end_index = element.get('endIndex')
            if end_index is not None:
                # Subtract 1 to avoid inserting at the absolute end, which may be invalid
                return max(1, end_index - 1)
        
        return 1  # Fallback if no valid endIndex is found
    except HttpError as err:
        print(f"Error getting document length: {err}")
        return 1
    except Exception as e:
        print(f"An unexpected error occurred getting document length: {e}")
        return 1

def write_content_to_doc(document_id, document_structure): # Renamed content_to_write to document_structure
    """Writes content based on a structured list to the Google Doc."""
    service = authenticate_docs_api()
    if not service:
        return

    try:
        current_doc_length = get_document_length(service, document_id)
        print(f"Current document length: {current_doc_length}")
        requests = []

        # Start with a new line if it's not an empty document
        if current_doc_length > 0:
            requests.append({
                'insertText': {
                    'location': {'index': current_doc_length},
                    'text': '\n\n'
                }
            })
            current_doc_length += 2

        for block in document_structure:
            block_type = block.get("type")
            text_to_insert = ""
            block_start_index = current_doc_length # Store for potential inline formatting

            if block_type == "heading":
                level = block.get("level", 1)
                heading_text = block.get("text", "No Heading")
                text_to_insert = heading_text + "\n" # Add newline for spacing
                requests.append({
                    'insertText': {
                        'location': {'index': current_doc_length},
                        'text': text_to_insert
                    }
                })
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': current_doc_length,
                            'endIndex': current_doc_length + len(text_to_insert),
                        },
                        'paragraphStyle': {
                            'namedStyleType': f'HEADING_{level}'
                        },
                        'fields': 'namedStyleType'
                    }
                })
                current_doc_length += len(text_to_insert)
                # Add an extra newline after heading for spacing if not the last block
                if document_structure.index(block) < len(document_structure) - 1:
                     requests.append({
                        'insertText': {
                            'location': {'index': current_doc_length},
                            'text': '\n'
                        }
                    })
                     current_doc_length += 1

            elif block_type == "paragraph":
                paragraph_text = block.get("text", "")
                text_to_insert = paragraph_text + "\n"
                requests.append({
                    'insertText': {
                        'location': {'index': current_doc_length},
                        'text': text_to_insert
                    }
                })
                # --- Here's where inline formatting logic would go ---
                # Example: Simple bold detection (more sophisticated regex needed for actual MD)
                # This is a very basic example; a full MD parser would be complex
                bold_matches = re.finditer(r'\*\*(.*?)\*\*', paragraph_text)
                for match in bold_matches:
                    bold_start_rel = match.start()
                    bold_end_rel = match.end()
                    # Adjust for the '\n' at the end of text_to_insert if it's included in calculation
                    # The actual text inserted is paragraph_text
                    bold_doc_start = block_start_index + bold_start_rel
                    bold_doc_end = block_start_index + bold_end_rel - 4 # Adjust for ** characters

                    # Replace **text** with text before inserting to avoid literal **
                    paragraph_text = paragraph_text.replace(match.group(0), match.group(1), 1)

                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': bold_doc_start,
                                'endIndex': bold_doc_end
                            },
                            'textStyle': {
                                'bold': True
                            },
                            'fields': 'bold'
                        }
                    })
                # If you modify text_to_insert (e.g., removing **), re-insert or recalculate length
                # For simplicity here, assume you pre-process text_to_insert
                # For actual inline MD, you'd insert plaintext and then apply formatting
                # For a full MD parser, you'd insert segments of text with different styles

                current_doc_length += len(text_to_insert)


            elif block_type == "list":
                list_items = block.get("items", [])
                for item in list_items:
                    list_item_text = f"• {item}\n" # For bullet points
                    requests.append({
                        'insertText': {
                            'location': {'index': current_doc_length},
                            'text': list_item_text
                        }
                    })
                    requests.append({
                        'createParagraphBullets': {
                            'range': {
                                'startIndex': current_doc_length,
                                'endIndex': current_doc_length + len(list_item_text)
                            },
                            'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                        }
                    })
                    current_doc_length += len(list_item_text)
                # Add an extra newline after list for spacing
                requests.append({
                    'insertText': {
                        'location': {'index': current_doc_length},
                        'text': '\n'
                    }
                })
                current_doc_length += 1

            elif block_type == "bold_note":
                note_text = block.get("text", "")
                text_to_insert = f'\n{note_text}\n'
                requests.append({
                    'insertText': {
                        'location': {'index': current_doc_length},
                        'text': text_to_insert
                    }
                })
                requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': current_doc_length,
                            'endIndex': current_doc_length + len(text_to_insert),
                        },
                        'textStyle': {
                            'bold': True
                        },
                        'fields': 'bold'
                    }
                })
                current_doc_length += len(text_to_insert)

            elif block_type == "code_block":
                code = block.get("code", "")
                language = block.get("language", "")
                code_text = f"{code.strip()}\n"
                requests.append({
                    'insertText': {
                        'location': {'index': current_doc_length},
                        'text': code_text
                    }
                })
                requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': current_doc_length,
                            'endIndex': current_doc_length + len(code_text),
                        },
                        'textStyle': {
                            'weightedFontFamily': {'fontFamily': 'Courier New'},
                            'backgroundColor': {
                                'color': {'rgbColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95}}
                            }
                        },
                        'fields': 'weightedFontFamily,backgroundColor'
                    }
                })
                current_doc_length += len(code_text)

            # Add more elif blocks for other types (image, table, etc.)

        result = service.documents().batchUpdate(
            documentId=document_id, body={'requests': requests}
        ).execute()
        print(f"Document updated successfully. Replies: {len(result.get('replies'))}")

    except HttpError as err:
        print(f"An API error occurred: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage with the new structure
content_data = [
    {"type": "heading", "level": 1, "text": "AI Report - Q3 2024"},
    {"type": "paragraph", "text": "This is a summary of the latest AI advancements. It covers key trends and their impact on the industry. This paragraph also contains italicized text."},
    {"type": "list", "items": ["Improved natural language understanding", "Advancements in generative AI models", "Increased adoption of AI in enterprise solutions"]},
    {"type": "bold_note", "text": "Further analysis and detailed data will be provided in a separate attachment."},
    {"type": "heading", "level": 2, "text": "Key Challenges"},
    {"type": "paragraph", "text": "One of the primary challenges is the ethical considerations surrounding AI deployment."}
]
# write_content_to_doc("YOUR_DOCUMENT_ID", content_data)

if __name__ == '__main__': 
    # Example content that your AI might generate (or a parsed Markdown file)
    # Replace with your actual key file path and document ID!
    # Ensure your service_account_key.json is in the correct directory
    # or provide its full path.
    # And the DOCUMENT_ID should be the ID from your Google Doc URL.
    if SERVICE_ACCOUNT_KEY_FILE  and  DOCUMENT_ID:
          # Assuming mdstring is defined in data.py
        data="# Sample Markdown content to be converted\n\n## Heading 1\nThis is a paragraph with **bold text** and *italic text"
        write_content_to_doc(DOCUMENT_ID, data) 
    else:
        print("\n*** IMPORTANT: Please update 'SERVICE_ACCOUNT_KEY_FILE' and 'DOCUMENT_ID' in the script! ***\n")