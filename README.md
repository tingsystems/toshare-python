# ToShare

Install
```sh
pip install -e git://github.com/tingsystems/toshare-python.git@master#egg=toshare
```
GET Template

```python
import toshare

toshare._credentials = ('client_id', 'client_secret')
# Get template by slug
template = toshare.Templates.get(template_name)
if template is None:
    print('Fail send notification template not found')

```

Send Message

```python
import toshare

toshare._credentials = ('client_id', 'client_secret')

message = toshare.Messages.create({
  'template': template.id,
  'subject': 'Hello',
  'data': {'firstName': 'Tony'},
  'to': email_to,
  'fromName': 'Company Inc.',
  'fromEmail': 'hello@company.com'
 })
 
if message.id:
    print('Notification send {} ok'.format(email_to))

```

## Library Development and Testing

You can test the toshare library with nose from the toshare library root:

```sh
$ nosetests
```
