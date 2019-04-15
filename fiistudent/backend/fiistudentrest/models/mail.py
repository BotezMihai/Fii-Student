import ndb_orm as ndb

class Mail(ndb.Model):

    """Subject and receiver of the email."""

    cc = ndb.StringProperty()
    bcc = ndb.StringProperty()
    subject = ndb.StringProperty()