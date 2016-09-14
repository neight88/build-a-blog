import webapp2, jinja2, os
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

class Post(db.Model):
    title = db.StringProperty(required = True)
    text = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class redirectHandler(Handler):
    def get(self):
        self.redirect("/blog")
    def post(self):
        self.redirect("/blog")

class MainPage(Handler):
    def render_front(self, title="", text="", error="", page="1"):
        #posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        page = int(page)
        limit = 5
        if page < 2:
            offset = 0
        else:
            offset = (page - 1) * 5
        posts = get_posts(limit, offset)
        totalNumberOfPosts = posts.count(offset=offset, limit=limit)
        if page < (totalNumberOfPosts / limit):
            nextPage=(page + 1)
        else:
            nextPage = ""
        self.render("front.html", title=title, text=text, error=error, posts=posts, page=page, nextPage=nextPage)
         #page and page for parents)

    def get(self):
        page = self.request.get("page")
        self.render_front(page=page)

class postPage(Handler):
    def render_page(self, title="", text="", error=""):
        self.render("newPostForm.html", title=title, text=text, error=error)

    def get(self):
        self.render_page()
    def post(self):
        title = self.request.get("form_title")
        text = self.request.get("form_text")

        if title and text:
            newPost = Post(title=title, text=text)
            newPost.put()
            self.redirect("/blog/" + str(newPost.key().id()))
        else:
            error = "We need both a title and some text"
            self.render_page(title, text, error)


class ViewPostHandler(Handler):
    def get(self, id):
        postID = Post.get_by_id(int(id))
        if postID:
            title = postID.title
            text = postID.text
            self.render("singlePost.html", title=title, text=text)

def get_posts(limit, offset):
    limit = str(limit)
    offset = str(offset)
    posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT "+limit+" OFFSET " + offset)
    return posts


app = webapp2.WSGIApplication([
    ('/', redirectHandler),
    ('/blog', MainPage),
    ('/newpost', postPage),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
