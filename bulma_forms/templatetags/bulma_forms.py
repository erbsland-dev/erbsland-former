#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import dataclass
from typing import Any

from django import forms
from django import template
from django.forms import BoundField
from django.template import RequestContext
from django.template.loader import get_template
from django.urls import reverse_lazy

from bulma_forms.tools import BULMA_LEFT_ICON_ATTR

register = template.Library()


@dataclass
class ElementClasses:
    """
    Classes to be applied to all form elements.
    """

    label = ""  # Additional classes for the label element.
    value = ""  # Additional classes for the value element.
    left_icon = ""  # Font awesome icon name for an icon on the left side of the control.


def widget_type(field: BoundField) -> str:
    widget = field.field.widget
    if isinstance(
        widget,
        (
            forms.TextInput,
            forms.NumberInput,
            forms.EmailInput,
            forms.PasswordInput,
            forms.URLInput,
        ),
    ):
        return "input"
    if isinstance(widget, forms.Textarea):
        return "textarea"
    if isinstance(widget, forms.SelectMultiple):
        return "multiple_select"
    if isinstance(widget, forms.Select):
        return "select"
    if isinstance(widget, forms.CheckboxSelectMultiple):
        return "multiple_checkbox"
    if isinstance(widget, forms.CheckboxInput):
        return "checkbox"
    if isinstance(widget, forms.RadioSelect):
        return "radio"
    if isinstance(widget, forms.FileInput):
        return "file"


def add_input_classes(field: BoundField):
    if widget_type(field) not in ["checkbox", "multiple_checkbox", "radio", "file"]:
        field_classes = set(field.field.widget.attrs.get("class", "").split())
        field_classes.add("control")
        field.field.widget.attrs["class"] = " ".join(sorted(field_classes))


def render_field(bound_field: BoundField, is_horizontal: bool = False):
    if not isinstance(bound_field, BoundField):
        raise ValueError("expected BoundField instance.")
    # Remove helper attributes
    element_classes = ElementClasses()
    if BULMA_LEFT_ICON_ATTR in bound_field.field.widget.attrs:
        element_classes.left_icon = bound_field.field.widget.attrs[BULMA_LEFT_ICON_ATTR]
        del bound_field.field.widget.attrs[BULMA_LEFT_ICON_ATTR]
    add_input_classes(bound_field)
    # Add classes for formsets
    if getattr(bound_field, "is_in_formset", False):
        element_classes.label += " is-hidden-tablet is-small"
        element_classes.value += " is-small"
    if value_classes := getattr(bound_field, "value_classes", None):
        element_classes.value += f" {value_classes}"
    widget_type_str = widget_type(bound_field)
    element_template = get_template(f"bulma_forms/{widget_type_str}_field.html")
    context = {
        "field": bound_field,
        "classes": element_classes,
        "form": bound_field.form,
        "is_horizontal": is_horizontal,
    }
    return element_template.render(context)


def prepare_form_and_context(context: dict, form) -> str:
    """
    Prepare the form fields and context to render a form.

    :param context: The context that is updated.
    :param form: The form to modify.
    :return: The template to render for the form.
    """
    for field in form.visible_fields():
        add_input_classes(field)
    context.update({"form": form})
    return "bulma_forms/form.html"


@register.filter
def bulma_render_with_class(field, css_class_to_add=""):
    """
    Render a field widget with additional classes added.
    """
    field_classes = field.field.widget.attrs.get("class", "").split()
    if css_class_to_add:
        field_classes.append(css_class_to_add)
    if getattr(field, "is_in_formset", False):
        field_classes.append("is-small")
    if value_classes := getattr(field, "value_classes", None):
        field_classes.extend(value_classes.split())
    if len(field.errors) > 0:
        field_classes.append("is-danger")
    field_classes = list(set(field_classes))
    field_classes.sort()
    return field.as_widget(attrs={"class": " ".join(field_classes)})


@register.filter
def bulma_flatten_help(text):
    """
    Flatten the HTML help text
    """
    text = str(text)
    if "<ul>" in text:
        text = text.replace("<ul>", "")
        text = text.replace("<li>", "")
        text = text.replace("</li>", "/n")
        text = "<br>".join(x.strip() for x in text.split("/n"))
    return text


@register.filter
def bulma_field(element):
    """
    Render a field with the correct style.
    """
    return render_field(element)


@register.filter
def bulma_horizontal_field(element):
    """
    Render a horizontal field with the correct style.
    """
    return render_field(element, is_horizontal=True)


@register.filter
def bulma_field_with_icon(element, left_icon_classes: str):
    """
    Render a field, form or formset with the correct style and with the given icon when possible.
    """
    element.widget.attrs["left_icon"] = left_icon_classes
    return render_field(element)


@register.inclusion_tag("bulma_forms/form/errors.html")
def bulma_form_errors(form):
    """
    Render form errors as notification.
    """
    return {"form": form}


@register.inclusion_tag("bulma_forms/form/button_text_with_icon.html")
def bulma_form_button_text(text: str, icon: str):
    """
    Render the text on a button and place the icon on the left or right side.

    :param text: The text to render.
    :param icon: The fontawesome icon classes to use.
    """
    icon_on_the_right_side = False
    if "-right" in icon:
        icon_on_the_right_side = True
    if icon == "play":
        icon_on_the_right_side = True
    return {"text": text, "icon": icon, "icon_on_the_right_side": icon_on_the_right_side}


@dataclass
class BulmaFormArgument:
    name: str
    value_type: type
    default: Any


BULMA_FORM_ARGUMENTS = [
    BulmaFormArgument("submit_text", str, ""),
    BulmaFormArgument("submit_class", str, "is-success"),
    BulmaFormArgument("submit_icon", str, ""),
    BulmaFormArgument("submit_enabled", bool, True),
    BulmaFormArgument("cancel_url", str, ""),
    BulmaFormArgument("cancel_page", str, ""),
    BulmaFormArgument("cancel_text", str, ""),
    BulmaFormArgument("cancel_class", str, ""),
    BulmaFormArgument("cancel_icon", str, ""),
    BulmaFormArgument("cancel_enabled", bool, True),
]


def update_context_for_form_render(context: RequestContext, form, visible_fields, **kwargs):
    new_context = {}
    form_with_file = False
    if callable(visible_fields):
        visible_fields = visible_fields()
    for field in visible_fields:
        if widget_type(field) == "file":
            form_with_file = True
            break
    new_context["form_with_file"] = form_with_file
    for arg in BULMA_FORM_ARGUMENTS:
        # Ignore this if the context already contains one of these arguments, and they are actually set to something.
        if arg.name in context:
            if arg.value_type is bool:
                continue
            if context[arg.name]:
                continue
        new_context[arg.name] = arg.default
        if hasattr(form, f"get_{arg.name}") and callable(getattr(form, f"get_{arg.name}")):
            value = getattr(form, f"get_{arg.name}")()
            new_context[arg.name] = arg.value_type(value)
        if hasattr(form, f"{arg.name}"):
            value = getattr(form, arg.name)
            new_context[arg.name] = arg.value_type(value)
        if arg.name in kwargs:
            value = kwargs[arg.name]
            new_context[arg.name] = arg.value_type(value)
    context.update(new_context)
    if context["cancel_page"]:
        if not context["cancel_url"]:
            context["cancel_url"] = reverse_lazy(context["cancel_page"])


@register.simple_tag(takes_context=True)
def bulma_form_begin(context: RequestContext, form, **kwargs):
    """
    Render just the beginning of the form HTML.
    """
    update_context_for_form_render(context, form, form.visible_fields(), **kwargs)
    context = dict(context.flatten())
    prepare_form_and_context(context, form)
    element_template = get_template("bulma_forms/form/begin.html")
    return element_template.render(context)


@register.simple_tag(takes_context=True)
def bulma_form_fields(context: RequestContext, form, **kwargs):
    """
    Render the fields of the form.
    """
    element_template = get_template("bulma_forms/form/fields.html")
    return element_template.render(context.flatten())


@register.simple_tag(takes_context=True)
def bulma_form_submit(context: RequestContext, form, **kwargs):
    """
    Render the submitting and cancel buttons for the form
    """
    element_template = get_template("bulma_forms/form/submit.html")
    return element_template.render(context.flatten())


@register.simple_tag(takes_context=True)
def bulma_form_end(context: RequestContext, form, **kwargs):
    """
    Render just the end of the form HTML.
    """
    element_template = get_template("bulma_forms/form/end.html")
    return element_template.render(context.flatten())


@register.simple_tag(takes_context=True)
def bulma_form(context: RequestContext, form, **kwargs):
    """
    Render a form with the correct style.

    Accepts the arguments 'submit_text', 'submit_class' and 'cancel_page'.
    """
    update_context_for_form_render(context, form, form.visible_fields, **kwargs)
    context = dict(context.flatten())
    template_path = prepare_form_and_context(context, form)
    element_template = get_template(template_path)
    return element_template.render(context)


@register.simple_tag(takes_context=True)
def bulma_formset(context: RequestContext, formset, **kwargs):
    """
    Render a formset with the correct style.
    """
    has_management = getattr(formset, "management_form", None)
    if not has_management:
        raise ValueError("This is no formset")
    labels = []
    field: forms.BoundField
    column_classes = []
    value_classes = []
    if len(formset) > 0:
        if "column_classes" in kwargs:
            column_classes = kwargs["column_classes"].split(",")
        while len(column_classes) < (len(formset[0].visible_fields())):
            column_classes.append("")
        if "value_classes" in kwargs:
            value_classes = kwargs["value_classes"].split(",")
        while len(value_classes) < (len(formset[0].visible_fields())):
            value_classes.append("")
        for index, field in enumerate(formset[0].visible_fields()):
            labels.append((field.label, column_classes[index]))
    for form in formset:
        for index, field in enumerate(form.visible_fields()):
            add_input_classes(field)
            field.is_in_formset = True
            field.column_classes = column_classes[index]
            field.value_classes = value_classes[index]
    context = context.flatten()
    context.update({"formset": formset, "formset_labels": labels})
    element_template = get_template("bulma_forms/form_set.html")
    return element_template.render(context)


@register.inclusion_tag("bulma_forms/control_button.html")
def bulma_control_button(text: str, url: str, button_class: str = "is-success", icon: str = ""):
    """
    A button link embedded in a control block.

    :param text: The text on the button.
    :param url: The URL for the link.
    :param button_class: The additional classes for the button element style.
    :param icon: The fontawesome icon name to display in the button.
    """
    return {
        "text": text,
        "url": url,
        "button_class": button_class,
        "icon": icon,
    }
