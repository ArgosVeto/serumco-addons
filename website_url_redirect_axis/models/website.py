# -*- coding: utf-8 -*-
import logging

from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo import api, models
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.osv.expression import FALSE_DOMAIN

logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = "website"

    def enumerate_pages(self, query_string=None, force=False):
        """Show redirected URLs in search results."""
        query = query_string or ""
        logger.info("query : %s",query)
        seo_redirections = list()
        redirection_records = self.env["website.seo.redirection"].search([
            "|", ("origin", "ilike", query),
            ("destination", "ilike", query),
        ])
        for record in redirection_records:
           for url in record.origin, record.destination:
                if url not in seo_redirections:
                    seo_redirections.append(url)
        # Give super() a website to work with
        #if not request.website_enabled:
        #     self.ensure_one()
        #     request.website = self
        #Yield super()'s pages
        for page in self.enumerate_pages_bis(query_string, force=True):
            try:
                seo_redirections.remove(page["loc"])
            except ValueError:
                pass
            yield page
        # Remove website if we were supposed to have none
        #if not request.website_enabled:
        #     request.website = None
        # Yield redirected pages not detected by super()
        for page in seo_redirections:
            yield {"loc": page}

    def enumerate_pages_bis(self, query_string=None, force=False):
        """ Available pages in the website/CMS. This is mostly used for links
            generation and can be overridden by modules setting up new HTML
            controllers for dynamic pages (e.g. blog).
            By default, returns template views marked as pages.
            :param str query_string: a (user-provided) string, fetches pages
                                     matching the string
            :returns: a list of mappings with two keys: ``name`` is the displayable
                      name of the resource (page), ``url`` is the absolute URL
                      of the same.
            :rtype: list({name: str, url: str})
        """

        router = request.httprequest.app.get_db_router(request.db)
        # Force enumeration to be performed as public user
        url_set = set()

        sitemap_endpoint_done = set()

        for rule in router.iter_rules():
            if 'sitemap' in rule.endpoint.routing:
                if rule.endpoint in sitemap_endpoint_done:
                    continue
                sitemap_endpoint_done.add(rule.endpoint)

                func = rule.endpoint.routing['sitemap']
                if func is False:
                    continue
#                for loc in func(self.env, rule, query_string):
#                    yield loc
#                continue

            if not self.rule_is_enumerable(rule):
                continue

            converters = rule._converters or {}
            if query_string and not converters and (query_string not in rule.build({}, append_unknown=False)[1]):
                continue

            values = [{}]
            # converters with a domain are processed after the other ones
            convitems = sorted(
                converters.items(),
                key=lambda x: (hasattr(x[1], 'domain') and (x[1].domain != '[]'), rule._trace.index((True, x[0]))))

            for (i, (name, converter)) in enumerate(convitems):
                newval = []
                for val in values:
                    query = i == len(convitems) - 1 and query_string
                    if query:
                        r = "".join([x[1] for x in rule._trace[1:] if not x[0]])  # remove model converter from route
                        query = sitemap_qs2dom(query, r, self.env[converter.model]._rec_name)
                        if query == FALSE_DOMAIN:
                            continue
                    for value_dict in converter.generate(uid=self.env.uid, dom=query, args=val):
                        newval.append(val.copy())
                        value_dict[name] = value_dict['loc']
                        del value_dict['loc']
                        newval[-1].update(value_dict)
                values = newval

            for value in values:
                domain_part, url = rule.build(value, append_unknown=False)
                if not query_string or query_string.lower() in url.lower():
                    page = {'loc': url}
                    if url in url_set:
                        continue
                    url_set.add(url)

                    yield page

        # '/' already has a http.route & is in the routing_map so it will already have an entry in the xml
        domain = [('url', '!=', '/')]
        if not force:
            domain += [('website_indexed', '=', True)]
            # is_visible
            domain += [('website_published', '=', True), '|', ('date_publish', '=', False), ('date_publish', '<=', fields.Datetime.now())]

        if query_string:
            domain += [('url', 'like', query_string)]

        pages = self.get_website_pages(domain)

        for page in pages:
            record = {'loc': page['url'], 'id': page['id'], 'name': page['name']}
            if page.view_id and page.view_id.priority != 16:
                record['priority'] = min(round(page.view_id.priority / 32.0, 1), 1)
            if page['write_date']:
                record['lastmod'] = page['write_date'].date()
            yield record


class SeoMetadata(models.AbstractModel):
    _inherit = 'website.seo.metadata'

    def _default_website_meta(self):
        res = super(SeoMetadata, self)._default_website_meta()
        company = request.website.company_id.sudo()
        title = (request.website or company).name
        if request.website.social_default_image:
            img = request.website.image_url(
                request.website, 'social_default_image')
        else:
            img = request.website.image_url(company, 'logo')
        full_url = request.httprequest.full_path.partition('?')
        full_url = full_url[0]
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        url = self.env['website.seo.redirection'].search(
            [("origin", "=", full_url)])
        for rec in url:
            full_url = rec.destination

        default_opengraph = {
            'og:type': 'website',
            'og:title': title,
            'og:site_name': company.name,
            'og:url': base_url+full_url,
            'og:image': img,
        }
        default_twitter = {
            'twitter:card': 'summary_large_image',
            'twitter:title': title,
            'twitter:image': img + '/300x300',
        }
        return {
            'default_opengraph': default_opengraph,
            'default_twitter': default_twitter,
        }
        return res


class WebsiteInherit(models.Model):
    _inherit = "website"

    def _get_canonical_url_localized(self, lang, canonical_params):
        res = super(WebsiteInherit, self)._get_canonical_url_localized(
            lang, canonical_params)
        full_url = request.httprequest.full_path.partition('?')
        full_url = full_url[0]
        url = self.env['website.seo.redirection'].search(
            [("origin", "=", full_url)])
        for rec in url:
            full_url = rec.destination
        return self.get_base_url() + full_url
        return res


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    def _compute_website_url(self):
        record = super(ProductTemplateInherit, self)._compute_website_url()
        for product in self:
            search_url = self.env['website.seo.redirection'].search(
                [('origin', '=', product.website_url)])
            if search_url.destination:
                product.website_url = search_url.destination
            else:
                product.website_url = "/shop/product/%s" % slug(product)

        return record
