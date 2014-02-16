import requests
def send_message(from_mail='foo@bar.com', to=None, subject=None, text=None, 
                        html=None, cc=None, bcc=None, ):
  if type(to) == type([]):
    to = [to]
  data = {}
  assert(to)
  assert(subject)
  assert(text or html)
  # subject = str(to) + ' ' + subject
  #tmp
 
      
  # data['to'] = ['dan@asseta.com']
  data['to'] = ''.join(to)
 
  data['from'] = from_mail
  data['subject'] = subject
  # data['subject'] = subject
  if text:
    data['text'] = text
  if html:
    data['html'] = html
  if cc:
    data['cc'] = cc
  if bcc == None:
    bcc = []
  if bcc:
    data['bcc'] = bcc

  data['api_user'] = 'iotasquared'
  data['api_key'] ='Calhack1'
  print 'sending message ' + str(data)

  return requests.post(
      "https://api.sendgrid.com/api/mail.send.json",
      data=data)
