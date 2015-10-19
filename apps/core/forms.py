__author__ = 'Junn'
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.contrib.admin.widgets import AdminFileWidget
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import url_params_from_lookup_dict
from django.contrib.admin.templatetags.admin_static import static
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.utils.text import Truncator
from django.utils.translation import ugettext as _


@python_2_unicode_compatible
class ErrorList(list):
    def __str__(self):
        return self.as_ul()

    def as_ul(self):
        if not self:
            return ''
        return format_html(u'<ul class="errorlist">{0}</ul>',
                           format_html_join('', u'<li><i class="icon-cancel-2"></i>{0}</li>',
                                            ((force_text(e),) for e in self))
                           )

    def as_text(self):
        if not self: return ''
        return '\n'.join(['* %s' % force_text(e) for e in self])

    def __repr__(self):
        return repr([force_text(e) for e in self])


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        print type(value), value
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            output.append('<a href="%s" target="_blank"><img src="%s" width=200 /></a>'
                          % (image_url, image_url))
        output.append(super(AdminFileWidget,
                            self).render(name, value, attrs))
        return mark_safe(u''.join(output))


class ForeignKeyRawIdWidget(forms.TextInput):
    """
    A Widget for displaying ForeignKeys in the "raw_id" interface rather than
    in a <select> box.
    """
    def __init__(self, rel, admin_site, attrs=None, using=None, extra={}):
        self.rel = rel
        self.admin_site = admin_site
        self.db = using
        self.extra = extra
        super(ForeignKeyRawIdWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        rel_to = self.rel.to
        if attrs is None:
            attrs = {}
        extra = []
        if rel_to in self.admin_site._registry:
            # The related object is registered with the same AdminSite
            related_url = reverse('admin:%s_%s_changelist' %
                                  (rel_to._meta.app_label,
                                   rel_to._meta.module_name),
                                  current_app=self.admin_site.name)

            params = self.url_parameters()
            if params:
                url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in params.items()])
            else:
                url = ''
            if "class" not in attrs:
                attrs['class'] = 'vForeignKeyRawIdAdminField' # The JavaScript code looks for this hook.
            # TODO: "lookup_id_" is hard-coded here. This should instead use
            # the correct API to determine the ID dynamically.
            extra.append('<a href="%s%s" class="related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);"> '
                            % (related_url, url, name))
            extra.append('<img src="%s" width="16" height="16" alt="%s" /></a>'
                            % (static('admin/img/selector-search.gif'), _('Lookup')))
        output = [super(ForeignKeyRawIdWidget, self).render(name, value, attrs)] + extra
        if value:
            output.append(self.label_for_value(value))
        return mark_safe(''.join(output))

    def base_url_parameters(self):
        return url_params_from_lookup_dict(self.rel.limit_choices_to)

    def url_parameters(self):
        from django.contrib.admin.views.main import TO_FIELD_VAR
        params = self.base_url_parameters()
        params.update(self.extra)
        params.update({TO_FIELD_VAR: self.rel.get_related_field().name})
        return params

    def label_for_value(self, value):
        key = self.rel.get_related_field().name
        try:
            obj = self.rel.to._default_manager.using(self.db).get(**{key: value})
            return '&nbsp;<strong>%s</strong>' % escape(Truncator(obj).words(14, truncate='...'))
        except (ValueError, self.rel.to.DoesNotExist):
            return ''