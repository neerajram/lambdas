import sys
import requests
from urllib3 import disable_warnings, exceptions
from tabulate import tabulate
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def lambda_handler(event=None, context=None):
    headers = ['URL', 'Status Code', 'Reason']
    error_url = []
    url_reasons = []
    status_codes = []

    f = open('urls.txt', "r", encoding='utf-8')
    urls = f.readlines()

    for url in urls:
        url = url.strip('\n')
        disable_warnings(exceptions.InsecureRequestWarning)
        # print(url)
        try:
            response = requests.head(url.encode('ascii', 'ignore'), timeout=5, verify=False, allow_redirects=True)
            status_code = response.status_code
            url_reason = response.reason
            print(url, status_code)
        except requests.exceptions.TooManyRedirects:
            print(url + ' Too many redirects')
            status_code = 000
            url_reason = 'Too many redirects'

        except requests.exceptions.ConnectionError:
            print(url + ' Connection Error')
            status_code = 000
            url_reason = 'Connection Error'

        except requests.exceptions.Timeout:
            print(url + ' Request timed out')
            status_code = 000
            url_reason = 'Request timed out'

        if status_code != 200:
            error_url.append(url)
            status_codes.append(status_code)
            url_reasons.append(url_reason)

    data = {'urls': error_url, 'Status Codes': status_codes, 'Reasons': url_reasons}
    # table = tabulate(data, headers, tablefmt="html")

    # send email only if any of the sites doesn't return 200
    if len(error_url) != 0:
        # print('Some URLs are not working, preparing to fail the function..')
        print('Some URLs are not working, preparing to send the email..')
        # This address must be verified.
        SENDER = 'support@wspuat.com'
        SENDERNAME = 'WSPUAT Support'

        # Replace recipient@example.com with a "To" address. If your account
        # is still in the sandbox, this address must be verified.
        RECIPIENT = 'ram.motaparthy.contractor@pepsico.com,Vijay.Ramachandran@pepsico.com,WebSolutionsSupport@pepsico.onmicrosoft.com'

        # Replace smtp_username with your Amazon SES SMTP user name.
        USERNAME_SMTP = "AKIAUWKO6U6XCMX63BXA"

        # Replace smtp_password with your Amazon SES SMTP password.
        PASSWORD_SMTP = "BCpf/5LeI8WERCO5eWfGg6rxqSMOzW2ngP7anii4NHlW"

        # (Optional) the name of a configuration set to use for this message.
        # If you comment out this line, you also need to remove or comment out
        # the "X-SES-CONFIGURATION-SET:" header below.
        # CONFIGURATION_SET = "ConfigSet"

        # If you're using Amazon SES in an AWS Region other than US West (Oregon),
        # replace email-smtp.us-west-2.amazonaws.com with the Amazon SES SMTP
        # endpoint in the appropriate region.
        HOST = "email-smtp.eu-west-1.amazonaws.com"
        PORT = 587

        # The subject line of the email.
        SUBJECT = 'ESSA: UAT Website down alert'

        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = ("The below sites are unresponsive\r\n"
                     "" + '\n'.join(error_url) + ""
                     )

        # The HTML body of the email.
        BODY_HTML = """
        <html><body>
        <img src="https://essa-website-alerting.s3.eu-central-1.amazonaws.com/pepsico1.png"  width="83" height="33" alt="logo" />
        <h2 style="font-family:Sans-serif" id="logo"><a > The below sites are unresponsive</a></h2>
        <style> 
            table, th, td {{ border: 1px solid black; border-collapse: collapse; }}
            th, td {{ padding: 5px; }}
        </style>
        {table}
        </body></html>
        """
        BODY_HTML = BODY_HTML.format(table=tabulate(data, headers, tablefmt="html"))

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        # Comment or delete the next line if you are not using a configuration set
        # msg.add_header('X-SES-CONFIGURATION-SET',CONFIGURATION_SET)

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(BODY_TEXT, 'plain')
        part2 = MIMEText(BODY_HTML, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        # msg.attach(part1)
        msg.attach(part2)

        # Try to send the message.
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            # stmplib docs recommend calling ehlo() before & after starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT.split(","), msg.as_string())
            server.close()
        # Display an error message if something goes wrong.
        except Exception as e:
            print("Error: ", e)
        else:
            print("Email sent!")
        sys.exit(1)
    else:
        print("All URLs are working")

