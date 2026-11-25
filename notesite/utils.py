def apply_bootstrap(form):
    """Add Bootstrap CSS classes to every widget of a form."""
    for field in form.fields.values():
        widget = field.widget
        css = "form-check-input" if getattr(widget, "input_type", None) == "checkbox" else "form-control"
        widget.attrs["class"] = f"{widget.attrs.get('class', '')} {css}".strip()
