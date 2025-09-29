"""
Document Generation System for Port Authority of India
Generates PDF approval documents for shipments
"""

import os
from datetime import datetime
from io import BytesIO
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF


class ApprovalDocumentGenerator:
    """Generate PDF approval documents for shipments"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        # Header style
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        # Body style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT
        )
        
        # Footer style
        self.footer_style = ParagraphStyle(
            'CustomFooter',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
    
    def generate_approval_document(self, shipment, approval_status, authority_user, reason=None):
        """
        Generate PDF approval document for a shipment
        
        Args:
            shipment: Shipment object
            approval_status: 'APPROVED' or 'REJECTED'
            authority_user: User who made the decision
            reason: Reason for rejection (if applicable)
        
        Returns:
            BytesIO: PDF document as bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Add header
        elements.extend(self._create_header())
        
        # Add title
        title_text = f"SHIPMENT {approval_status.upper()} CERTIFICATE"
        title = Paragraph(title_text, self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Add shipment details
        elements.extend(self._create_shipment_details(shipment))
        
        # Add approval details
        elements.extend(self._create_approval_details(approval_status, authority_user, reason))
        
        # Add footer
        elements.extend(self._create_footer())
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer and return it
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf
    
    def _create_header(self):
        """Create document header with logo and organization info"""
        elements = []
        
        # Organization header
        header_data = [
            ['PORT AUTHORITY OF INDIA', ''],
            ['Remote Secure File Storage System', ''],
            ['Document Generated: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '']
        ]
        
        header_table = Table(header_data, colWidths=[4*inch, 2*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 16),
            ('FONTNAME', (0, 1), (0, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (0, 1), 12),
            ('FONTNAME', (0, 2), (0, 2), 'Helvetica'),
            ('FONTSIZE', (0, 2), (0, 2), 10),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.darkblue),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        # Add horizontal line
        line_data = [['', '']]
        line_table = Table(line_data, colWidths=[6*inch])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 2, colors.darkblue),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_shipment_details(self, shipment):
        """Create shipment details section"""
        elements = []
        
        # Section header
        header = Paragraph("SHIPMENT DETAILS", self.header_style)
        elements.append(header)
        
        # Shipment details table
        details_data = [
            ['Shipment ID:', shipment.shipmentId],
            ['Cargo Type:', shipment.Cargo_Type],
            ['Cargo Name:', shipment.Cargo_Name],
            ['Source:', shipment.Source],
            ['Destination:', shipment.Destination],
            ['Shipper Name:', shipment.Shipper_Name],
            ['Shipper Company:', shipment.Shipment_Company],
            ['Receiver:', shipment.Receiver_Name],
            ['Created By:', shipment.created_by.email if shipment.created_by else 'N/A'],
            ['Created Date:', shipment.created_at.strftime('%Y-%m-%d %H:%M:%S')],
            ['Current Status:', shipment.status],
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ]))
        
        elements.append(details_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_approval_details(self, approval_status, authority_user, reason=None):
        """Create approval/rejection details section"""
        elements = []
        
        # Section header
        header_text = "APPROVAL DETAILS" if approval_status == 'APPROVED' else "REJECTION DETAILS"
        header = Paragraph(header_text, self.header_style)
        elements.append(header)
        
        # Approval details
        approval_data = [
            ['Decision:', approval_status.upper()],
            ['Authority:', authority_user.email if authority_user else 'N/A'],
            ['Decision Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ]
        
        if reason and approval_status == 'REJECTED':
            approval_data.append(['Reason:', reason])
        
        approval_table = Table(approval_data, colWidths=[2*inch, 4*inch])
        approval_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('BACKGROUND', (1, 0), (1, 0), colors.lightgreen if approval_status == 'APPROVED' else colors.lightcoral),
        ]))
        
        elements.append(approval_table)
        elements.append(Spacer(1, 30))
        
        # Add signature section
        signature_text = f"""
        <para align=center>
        <b>DIGITAL SIGNATURE</b><br/>
        This document has been digitally signed by {authority_user.email if authority_user else 'Authority'}<br/>
        Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}<br/>
        Document ID: DOC-{datetime.now().strftime('%Y%m%d%H%M%S')}
        </para>
        """
        signature = Paragraph(signature_text, self.body_style)
        elements.append(signature)
        
        return elements
    
    def _create_footer(self):
        """Create document footer"""
        elements = []
        
        elements.append(Spacer(1, 30))
        
        footer_text = """
        <para align=center>
        This is a computer-generated document and does not require a physical signature.<br/>
        Port Authority of India - Remote Secure File Storage System<br/>
        For verification, please contact the issuing authority.
        </para>
        """
        footer = Paragraph(footer_text, self.footer_style)
        elements.append(footer)
        
        return elements


def generate_approval_pdf(shipment, approval_status, authority_user, reason=None):
    """
    Convenience function to generate approval PDF
    
    Returns:
        HttpResponse: PDF response ready for download
    """
    generator = ApprovalDocumentGenerator()
    pdf_data = generator.generate_approval_document(shipment, approval_status, authority_user, reason)
    
    # Create HTTP response
    response = HttpResponse(pdf_data, content_type='application/pdf')
    filename = f"shipment_{shipment.shipmentId}_{approval_status.lower()}_certificate.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
