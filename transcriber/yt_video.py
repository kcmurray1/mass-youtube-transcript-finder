class YtVideo:

    def __init__(self, title, owner, upload_date, url):
        self.title = title
        self.owner = owner
        self.url = url
        self.date = upload_date

    def as_json(self):
        return {"title" :self.title, "owner": self.author, "url": self.url}
    
    
    def __str__(self):
        return f'Title: {self.title} by {self.owner} on {self.date} url: {self.url}' 
        
    



