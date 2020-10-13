from odoo.http import request
from odoo import fields, http, _
from odoo.addons.website_blog.controllers.main import WebsiteBlog
import werkzeug
from odoo.addons.website.controllers.main import QueryURL

class WebsiteBlog(WebsiteBlog):
	@http.route([
		'/blog',
		'/blog/page/<int:page>',
		'/blog/tag/<string:tag>',
		'/blog/tag/<string:tag>/page/<int:page>',
		'''/blog/<model("blog.blog", "[('website_id', 'in', (False, current_website_id))]"):blog>''',
		'''/blog/<model("blog.blog"):blog>/page/<int:page>''',
		'''/blog/<model("blog.blog"):blog>/tag/<string:tag>''',
		'''/blog/<model("blog.blog"):blog>/tag/<string:tag>/page/<int:page>''',
	], type='http', auth="public", website=True)
	def blog(self, blog=None, tag=None, page=1, **opt):
		Blog = request.env['blog.blog']
		if blog and not blog.can_access_from_current_website():
			raise werkzeug.exceptions.NotFound()
		blogs = Blog.search(request.website.website_domain(), order="create_date asc, id asc")
		if not blog and len(blogs) == 1:
			return werkzeug.utils.redirect('/blog/%s' % slug(blogs[0]), code=302)

		date_begin, date_end, state = opt.get('date_begin'), opt.get('date_end'), opt.get('state')

		values = self._prepare_blog_values(blogs=blogs, blog=blog, date_begin=date_begin, date_end=date_end, tags=tag, state=state, page=page)
		if isinstance(values, werkzeug.wrappers.Response):
			return values
		if blog:
			values['main_object'] = blog
			values['edit_in_backend'] = True
			values['blog_url'] = QueryURL('', ['blog', 'tag'], blog=blog, tag=tag, date_begin=date_begin, date_end=date_end)
		else:
			values['blog_url'] = QueryURL('/blog', ['tag'], date_begin=date_begin, date_end=date_end)
		if 'blog_blog' in opt and opt['blog_blog']:
			values['posts'] = values['posts'].filtered(lambda s:s.blog_id.id == int(opt['blog_blog']))
		blog_tag_ids = request.env['blog.tag'].sudo().search([])
		if 'blog_tag' in opt and opt['blog_tag']:
			values['posts'] = values['posts'].filtered(lambda s:int(opt['blog_tag']) in s.tag_ids.ids)
		values.update({'blog_tag_ids':blog_tag_ids})
		return request.render("website_blog.blog_post_short", values)