from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Filtro para agregar clases CSS a los widgets de un formulario.
    """
    if hasattr(field, 'field'):
        existing_classes = field.field.widget.attrs.get('class', '')
        field.field.widget.attrs['class'] = f'{existing_classes} {css_class}'.strip()
    return field
