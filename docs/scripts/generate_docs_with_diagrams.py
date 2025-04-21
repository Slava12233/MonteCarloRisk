#!/usr/bin/env python
"""
Generate comprehensive HTML documentation from all Markdown files in the docs directory.
This script converts all Markdown files to HTML and creates an index page linking to all documents.
Includes support for Mermaid diagrams.
"""

import markdown
import os
import shutil
import re
from datetime import datetime

# Configuration
DOCS_DIR = "docs"
OUTPUT_DIR = "html_docs"
EXCLUDED_FILES = ["index.md"]  # Files to exclude from conversion
TITLE = "Google ADK Agent Starter Kit - Documentation"
PROJECT_NAME = "MonteCarloRisk_AI"
CSS_FILENAME = "style.css"

def ensure_dir_exists(dir_path):
    """Ensure a directory exists, create it if it doesn't."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")

def create_css_file(output_dir):
    """Create a CSS file for styling the HTML documentation."""
    css_content = """
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .sidebar {
        position: fixed;
        width: 250px;
        height: 100%;
        overflow: auto;
        padding: 20px;
        border-right: 1px solid #ddd;
    }
    
    .content {
        margin-left: 290px;
        padding: 20px;
    }
    
    @media screen and (max-width: 900px) {
        .sidebar {
            position: relative;
            width: auto;
            height: auto;
            border-right: none;
            border-bottom: 1px solid #ddd;
            margin-bottom: 20px;
        }
        .content {
            margin-left: 0;
        }
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
        margin-top: 24px;
    }
    
    a {
        color: #3498db;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    pre {
        background-color: #f8f8f8;
        border-radius: 3px;
        font-size: 85%;
        padding: 16px;
        overflow: auto;
    }
    
    code {
        background-color: #f8f8f8;
        border-radius: 3px;
        font-size: 85%;
        padding: 0.2em 0.4em;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }
    
    th, td {
        border: 1px solid #ddd;
        padding: 8px 12px;
        text-align: left;
    }
    
    th {
        background-color: #f2f2f2;
    }
    
    blockquote {
        border-left: 4px solid #ddd;
        padding-left: 16px;
        color: #666;
        margin-left: 0;
    }
    
    .navbar {
        background-color: #2c3e50;
        color: white;
        padding: 10px 20px;
        margin-bottom: 20px;
        border-radius: 5px;
    }
    
    .navbar h1 {
        margin: 0;
        color: white;
    }
    
    .document-list {
        list-style-type: none;
        padding: 0;
    }
    
    .document-list li {
        margin-bottom: 10px;
        padding: 5px;
        border-bottom: 1px solid #eee;
    }
    
    .document-list li:last-child {
        border-bottom: none;
    }
    
    .footer {
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #ddd;
        text-align: center;
        font-size: 0.9em;
        color: #777;
    }

    /* Mermaid diagram styling */
    .mermaid {
        margin: 20px 0;
        text-align: center;
    }
    """
    
    css_path = os.path.join(output_dir, CSS_FILENAME)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print(f"Created CSS file: {css_path}")
    return CSS_FILENAME

def process_mermaid_diagrams(md_content):
    """
    Pre-process Mermaid diagrams in Markdown content by making them compatible 
    with mermaid.js rendering in the browser.
    """
    # Define pattern to find ```mermaid blocks
    pattern = r'```mermaid\s+([\s\S]+?)\s+```'
    
    # Replace each match with a div that Mermaid.js can render
    return re.sub(pattern, r'<div class="mermaid">\n\1\n</div>', md_content)

def convert_md_to_html(input_file, output_file, css_file):
    """Convert a Markdown file to HTML."""
    print(f"Converting {input_file} to {output_file}")
    
    # Read the markdown file
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Process Mermaid diagrams
    md_content = process_mermaid_diagrams(md_content)
    
    # Get the title from the first line if it's a heading
    title = os.path.basename(input_file).replace('.md', '')
    if md_content.startswith('# '):
        title = md_content.split('\n')[0].replace('# ', '')
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.attr_list'
        ]
    )
    
    # Add basic styling, navigation, and Mermaid.js
    styled_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - {PROJECT_NAME}</title>
        <link rel="stylesheet" href="{css_file}">
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'default',
                    securityLevel: 'loose',
                    flowchart: {{ useMaxWidth: false }}
                }});
            }});
        </script>
    </head>
    <body>
        <div class="navbar">
            <h1>{PROJECT_NAME}</h1>
            <p><a href="index.html" style="color: white;">← Back to Documentation Index</a></p>
        </div>
        
        {html_content}
        
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><a href="index.html">Back to Documentation Index</a></p>
        </div>
    </body>
    </html>
    """
    
    # Write the HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(styled_html)
    
    print(f"Conversion complete: {output_file}")
    return title

def create_index_page(docs, output_dir, css_file):
    """Create an index.html page that links to all the documentation files."""
    index_path = os.path.join(output_dir, "index.html")
    
    # Sort docs by name for better organization
    sorted_docs = sorted(docs.items(), key=lambda x: x[0])
    
    # Group documents by category based on filename patterns
    categories = {
        "Main Documentation": [],
        "Deployment Guides": [],
        "Technical Guides": [],
        "Project Management": [],
        "Other": []
    }
    
    for filename, title in sorted_docs:
        if "PLANNING" in filename or "README" in filename or "DOCUMENTATION" in filename:
            categories["Main Documentation"].append((filename, title))
        elif "DEPLOY" in filename or "ENGINE" in filename:
            categories["Deployment Guides"].append((filename, title))
        elif "PYDANTIC" in filename or "visualization" in filename:
            categories["Technical Guides"].append((filename, title))
        elif "ACTION" in filename or "TASK" in filename:
            categories["Project Management"].append((filename, title))
        else:
            categories["Other"].append((filename, title))
    
    # Build the HTML content for the index page
    doc_list_html = ""
    for category, items in categories.items():
        if items:  # Only include non-empty categories
            doc_list_html += f"<h2>{category}</h2>\n<ul class='document-list'>\n"
            for filename, title in items:
                doc_list_html += f"    <li><a href='{filename}'>{title}</a></li>\n"
            doc_list_html += "</ul>\n"
    
    # Create the complete HTML
    index_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{TITLE}</title>
        <link rel="stylesheet" href="{css_file}">
    </head>
    <body>
        <div class="navbar">
            <h1>{PROJECT_NAME} - Documentation</h1>
        </div>
        
        <h1>Documentation Index</h1>
        <p>Welcome to the comprehensive documentation for the {PROJECT_NAME} project. 
        This documentation provides detailed information about the project's architecture, 
        deployment processes, and usage examples.</p>
        
        {doc_list_html}
        
        <div class="footer">
            <p>Documentation generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"Created index page: {index_path}")

def copy_project_readme(docs_dir, output_dir, css_file):
    """Copy and convert the project README to HTML."""
    readme_path = "README.md"
    if os.path.exists(readme_path):
        output_file = os.path.join(output_dir, "README.html")
        title = convert_md_to_html(readme_path, output_file, css_file)
        return {"README.html": title}
    return {}

def copy_task_file(docs_dir, output_dir, css_file):
    """Copy and convert the TASK.md file to HTML."""
    task_path = "TASK.md"
    if os.path.exists(task_path):
        output_file = os.path.join(output_dir, "TASK.html")
        title = convert_md_to_html(task_path, output_file, css_file)
        return {"TASK.html": title}
    return {}

def main():
    """Main function to generate HTML documentation."""
    print(f"Generating HTML documentation from {DOCS_DIR}...")
    
    # Ensure output directory exists
    ensure_dir_exists(OUTPUT_DIR)
    
    # Create CSS file
    css_file = create_css_file(OUTPUT_DIR)
    
    # Track all generated documents for the index
    all_docs = {}
    
    # Add README from project root
    readme_docs = copy_project_readme(DOCS_DIR, OUTPUT_DIR, css_file)
    all_docs.update(readme_docs)
    
    # Add TASK.md from project root
    task_docs = copy_task_file(DOCS_DIR, OUTPUT_DIR, css_file)
    all_docs.update(task_docs)
    
    # Process all .md files in the docs directory
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith('.md') and filename not in EXCLUDED_FILES:
            input_file = os.path.join(DOCS_DIR, filename)
            output_file = os.path.join(OUTPUT_DIR, filename.replace('.md', '.html'))
            
            title = convert_md_to_html(input_file, output_file, css_file)
            all_docs[filename.replace('.md', '.html')] = title
    
    # Create index page
    create_index_page(all_docs, OUTPUT_DIR, css_file)
    
    print(f"\nDocumentation generation complete! Open {os.path.join(OUTPUT_DIR, 'index.html')} to view.")
    print("Make sure to view the documentation in a web browser to see the rendered diagrams.")

if __name__ == "__main__":
    main() 