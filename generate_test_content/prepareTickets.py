# Run the script:
# python prepareTickets.py tickets.txt ./../document_bucket

import re
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os


def parse_ticket_file(filepath):
    """Parse the ticket file and return a dictionary organized by day."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by day delimiter
    day_pattern = r'=+\s*DAY\s+(\d+)\s*=+'
    days = re.split(day_pattern, content)
    
    # Organize into dictionary
    tickets_by_day = {}
    for i in range(1, len(days), 2):
        day_num = days[i]
        day_content = days[i + 1].strip()
        
        if day_content:
            tickets_by_day[int(day_num)] = parse_day_tickets(day_content)
    
    return tickets_by_day


def parse_day_tickets(day_content):
    """Parse individual tickets from a day's content."""
    tickets = []
    ticket_pattern = r'Ticket ID: (IT-\d+)\s+System: (.+?)\s+Issue: (.+?)\s+Resolution: (.+?)(?=\n\nTicket ID:|\Z)'
    
    matches = re.finditer(ticket_pattern, day_content, re.DOTALL)
    
    for match in matches:
        ticket = {
            'id': match.group(1).strip(),
            'system': match.group(2).strip(),
            'issue': match.group(3).strip(),
            'resolution': match.group(4).strip()
        }
        tickets.append(ticket)
    
    return tickets


def create_json_export(tickets_by_day, output_dir):
    """Create a JSON file with all ticket data."""
    # Flatten the data structure for JSON export
    all_tickets = []
    
    for day_num in sorted(tickets_by_day.keys()):
        for ticket in tickets_by_day[day_num]:
            ticket_data = {
                'ticket_id': ticket['id'],
                'issue': ticket['issue'],
                'resolution': ticket['resolution'],
                'day': day_num,
                'system': ticket['system']
            }
            all_tickets.append(ticket_data)
    
    # Write to JSON file
    json_filepath = os.path.join(output_dir, 'tickets_export.json')
    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(all_tickets, f, indent=2, ensure_ascii=False)
    
    print(f"Created JSON export: {json_filepath}")
    print(f"Total tickets in JSON: {len(all_tickets)}")
    return json_filepath


def create_pdf_for_day(day_num, tickets, output_dir):
    """Create a PDF for a specific day's tickets."""
    filename = os.path.join(output_dir, f'IT_Tickets_Day_{day_num:02d}.pdf')
    doc = SimpleDocTemplate(filename, pagesize=letter,
                           topMargin=0.75*inch, bottomMargin=0.75*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#2C3E50',
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#34495E',
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    ticket_header_style = ParagraphStyle(
        'TicketHeader',
        parent=styles['Heading3'],
        fontSize=12,
        textColor='#2980B9',
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    field_label_style = ParagraphStyle(
        'FieldLabel',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#7F8C8D',
        fontName='Helvetica-Bold',
        spaceAfter=2
    )
    
    field_value_style = ParagraphStyle(
        'FieldValue',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#2C3E50',
        spaceAfter=12,
        leftIndent=20
    )
    
    # Add title
    title = Paragraph(f"IT Support Tickets - Day {day_num}", title_style)
    elements.append(title)
    
    subtitle = Paragraph(f"Total Tickets: {len(tickets)}", subtitle_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add tickets
    for i, ticket in enumerate(tickets, 1):
        # Ticket header
        header = Paragraph(f"{ticket['id']} - {ticket['system']}", ticket_header_style)
        elements.append(header)
        
        # Issue
        issue_label = Paragraph("<b>Issue:</b>", field_label_style)
        elements.append(issue_label)
        issue_text = Paragraph(ticket['issue'], field_value_style)
        elements.append(issue_text)
        
        # Resolution
        resolution_label = Paragraph("<b>Resolution:</b>", field_label_style)
        elements.append(resolution_label)
        resolution_text = Paragraph(ticket['resolution'], field_value_style)
        elements.append(resolution_text)
        
        # Add spacing between tickets
        if i < len(tickets):
            elements.append(Spacer(1, 0.2*inch))
            # Add page break every 3 tickets for better readability
            if i % 3 == 0:
                elements.append(PageBreak())
    
    # Build PDF
    doc.build(elements)
    print(f"Created: {filename}")
    return filename


def main():
    """Main function to process tickets and generate PDFs and JSON."""
    import sys
    
    # Check if input file is provided
    if len(sys.argv) < 2:
        print("Usage: python ticket_to_pdf.py <input_file.txt> [output_directory]")
        print("\nExample: python ticket_to_pdf.py tickets.txt ./output")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './ticket_pdfs'
    
    # Validate input file
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Processing tickets from: {input_file}")
    print(f"Output directory: {output_dir}\n")
    
    # Parse tickets
    tickets_by_day = parse_ticket_file(input_file)
    
    if not tickets_by_day:
        print("No tickets found in the file!")
        sys.exit(1)
    
    print(f"Found {len(tickets_by_day)} days of tickets\n")
    
    # Generate JSON export
    print("Creating JSON export...")
    json_file = create_json_export(tickets_by_day, output_dir)
    print()
    
    # Generate PDFs
    print("Creating PDF files...")
    created_files = []
    for day_num in sorted(tickets_by_day.keys()):
        tickets = tickets_by_day[day_num]
        print(f"Processing Day {day_num}: {len(tickets)} tickets")
        pdf_file = create_pdf_for_day(day_num, tickets, output_dir)
        created_files.append(pdf_file)
    
    print(f"\n✓ Successfully created {len(created_files)} PDF files in '{output_dir}'")
    print(f"✓ JSON export saved to '{json_file}'")


if __name__ == "__main__":
    main()