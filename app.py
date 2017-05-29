from flask import Flask, redirect, url_for, request, render_template, Response
import os
import json
import requests
from multiprocessing import Pool
import sendgrid
from sendgrid.helpers.mail import *

app = Flask(__name__)


def send_mail(form_msg, form_name, form_email):

    sg = sendgrid.SendGridAPIClient(apikey=os.environ['SENDGRID_API_KEY'])
    # print("init")
    from_email = Email(form_email)
    # print("email init")
    to_email = Email(os.environ['KOSS_EMAIL'])
    # print("email init2")
    subject = "Query"
    # print("subject")
    content = Content("text/plain", "Query sent by:- " + form_name + "\n\n\n" +
                      "Message:- " + form_msg + "\n")
    # print("content")
    mail = Mail(from_email=from_email, subject=subject,
                to_email=to_email, content=content)
    # print("mail init")
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
        # print("sent")
    except urllib.HTTPError:
        print("not sent")
    except Exception:
        print("Some other exception occured. Not sent")


    from_email = Email(os.environ['KOSS_EMAIL'])
    # print("email init")
    to_email = Email(form_email)
    # print("email init2")
    subject = "Query Recieved"
    # print("subject")
    content = Content("text/plain", "Hi "+form_name+",\n\n"+"Your message has been recieved by us and we will respond to it soon."+"\nThank-you for communicating with us, hope your query will cleared by our team."+"\n\n\nKOSS IIT Kharagpur")
    # print("content")
    mail = Mail(from_email=from_email, subject=subject,
                to_email=to_email, content=content)
    # print("mail init")
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
        # print("sent")
    except urllib.HTTPError:
        print("not sent")
    except Exception:
        print("Some other exception occured. Not sent")

    
    slack_notifier(form_msg, form_name, form_email)    
    return None


# slack notifier module
def slack_notifier(form_msg, form_name, form_email,count=0):
    headers = {"Content-Type": "application/json"}

    data = json.dumps({"text": "Query from "+form_name+"<"+form_email+">\n\n"+"QUERY : "+form_msg+"\n\nPlease respond soon."})
       
    r = requests.post(os.environ["SLACK_WEBHOOK_URL"], headers=headers, data=data)

    if r.status_code!=200:
        if count<=2:
            print("error "+str(r.status_code)+" !!! trying again")
            count+=1
            slack_notifier(form_msg, form_name, form_email,count)
        else:
            print("terminated!!!")
    else:
        print("notification sent!!!")



@app.route('/mail', methods=['POST'])
def mail():
    pool = Pool(processes=10)
    r = pool.apply_async(
        send_mail, [request.form['msg'],
                    request.form['name'],
                    request.form['email']])
    return ("sent", 200, {'Access-Control-Allow-Origin': '*'})


@app.route('/captcha', methods=['POST'])
def captcha():
    t = json.loads(request.data.decode("utf-8"))
    gcaptcha = t['gcaptcha']
    r = requests.post("https://www.google.com/recaptcha/api/siteverify",
                      data={'secret': os.environ['KEY'], 'response': gcaptcha})
    if json.loads(r.content.decode('utf-8'))['success'] is True:
        return ("sent", 200, {'Access-Control-Allow-Origin': '*'})
    else:
        return ("Not sent", 400, {'Access-Control-Allow-Origin': '*'})


# if __name__ == "__main__":  # This is for local testin
#     app.run(host='localhost', port=3453, debug=True)


if __name__ == "__main__":  # This will come in use when
    port = int(os.environ.get("PORT", 5000))  # the app is deployed on heroku
    app.run(host='0.0.0.0', port=port, debug=True)
