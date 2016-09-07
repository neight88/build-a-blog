import webapp2
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.write(*args, **kwargs)

    def render_str(self, template, **parameters):
        t = jinja_env.get_template(template)
        return t.render(**parameters)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    text = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_front(self, title="", text="", error=""):
        posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("front.html", title=title, text=text, error=error, posts=posts)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("form_title")
        text = self.request.get("form_text")
        #art = self.request.get("art")
        if title and blogText:
            newPost = blog(title=title, text=text)
            newPost.put()
            self.redirect("/")
        else:
            error = "We need both a title and some text"
            self.render_front(title, blogText, error)

class postPage(Handler):
    def render_page(self, title="", text="", error=""):
        self.render("newPostForm.html", title=title, text=text, error=error)

    def get(self):
        self.render_page()
    def post(self):
        title = self.request.get("form_title")
        text = self.request.get("form_text")

        if title and text:
            newPost = Blog(title=title, text=text)
            newPost.put()
            self.redirect("/")
        else:
            error = "We need both a title and some text"
            self.render_page(title, text, error)


class ViewPostHandler(Handler):
    def get(self, id):
        staticPostID = Blog.get_by_id(int(id))
        #This does not actually display anything when you use the ID
        self.response.write(str(staticPostID))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', postPage),
    (webapp2.Route('/blog/<id:\d+>', ViewPostHandler))
], debug=True)
