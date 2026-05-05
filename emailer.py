import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import markdown
load_dotenv()

def send_email_newsletter(content):
    """
    Sends the AI news summary via email.
    """
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")
    email_receiver = os.getenv("EMAIL_RECEIVER")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not all([email_user, email_password, email_receiver]):
        print("Error: Email credentials missing in environment variables.")
        return False

    # Create the email message
    message = MIMEMultipart()
    message["From"] = email_user
    message["To"] = email_receiver
    message["Subject"] = "Daily AI News Summary"

    # Convert Markdown to HTML with table support
    html_content = markdown.markdown(content, extensions=['tables'])
    
    # Create a nice HTML template
    html_template = f"""
    <html>
      <head>
        <style>
          body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6; 
            color: #e2e8f0; 
            background-color: #f1f5f9; /* Outer background to contrast the dark container */
            margin: 0;
            padding: 40px 20px;
          }}
          .container {{
            max-width: 680px;
            margin: 0 auto;
            background-color: #1e293b; /* Dark slate background */
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
          }}
          p, span, div {{
            color: #e2e8f0;
          }}
          blockquote, em, i {{
            color: #94a3b8 !important;
            font-style: italic;
          }}
          h1.main-title {{ 
            color: #f8fafc; 
            text-align: center;
            border-bottom: 1px solid #334155;
            padding-bottom: 20px;
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 26px;
            font-weight: 700;
          }}
          .auto-note {{
            text-align: center;
            color: #64748b;
            font-size: 0.9em;
            font-style: italic;
            margin-bottom: 30px;
          }}
          h2 {{
            color: #38bdf8;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 22px;
          }}
          h3 {{ 
            color: #38bdf8; 
            margin-top: 25px;
            margin-bottom: 5px;
            font-size: 20px;
          }}
          h3 a, h2 a {{ 
            color: #38bdf8 !important; 
            text-decoration: none; 
          }}
          h3 a:hover, h2 a:hover {{ text-decoration: underline; }}
          
          .source {{ 
            color: #cbd5e1 !important; 
            font-size: 0.85em; 
            display: block;
            margin-bottom: 12px;
          }}
          .source b {{
            color: #e2e8f0;
          }}
          .summary {{ 
            margin-bottom: 25px; 
            color: #cbd5e1;
            background-color: #273548; /* Slightly lighter than container */
            padding: 16px;
            border-left: 4px solid #38bdf8;
            border-radius: 4px;
            font-size: 0.95em;
          }}
          hr {{
            border: 0;
            height: 1px;
            background: #334155;
            margin: 30px 0;
          }}
          .footer {{
            text-align: center;
            margin-top: 40px;
            font-size: 0.85em;
            color: #64748b;
          }}
          /* Table Styles */
          table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 0.95em;
            color: #e2e8f0;
          }}
          table th, table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #334155;
          }}
          table th {{
            color: #38bdf8;
            font-weight: 600;
            border-bottom: 2px solid #334155;
          }}
          table tr:hover {{
            background-color: #273548;
          }}
          table td:first-child {{
            color: #94a3b8;
          }}
          table td:nth-child(2) {{
            font-weight: bold;
            color: #f8fafc;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <h1 class="main-title">🚀 Daily AI News Summary</h1>
          <div class="auto-note">Note: This is an automatically generated digest.</div>
          
          {html_content}
          
          <div class="footer">
            <p>Sent by Daily AI News Bot 🤖</p>
          </div>
        </div>
      </body>
    </html>
    """
    message.attach(MIMEText(html_template, "html"))

    try:
        # Connect to the SMTP server and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls() # Secure the connection
            server.login(email_user, email_password)
            server.send_message(message)
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False