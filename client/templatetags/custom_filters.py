from django import template
import six # string manipulation
import pytz

register = template.Library()

@register.filter(name='cut')
def cut(value, arg):
    """Removes all values of arg from the given string"""
    return value.replace(arg, '')

@register.filter(name='split')
def split(value):
    """split string depending upon the argument passed"""
    if isinstance(value, six.string_types):
        string = value
    else:
        string = str(value)

    # convert to list with striping text
    if string:
        list = [x.strip() for x in string.split(',')]
        #print(list)
    else:
        list = None
    return list

@register.filter(name='ifinlist_dict')
def ifinlist_dict(value, list_of_dicts):
    """ return true if value exist in list """
    value = str(value)
    #print(value)
    #print(list_of_dicts)
    if list_of_dicts:
        for dict in list_of_dicts:
            original_txt = dict.get("original_txt")
            if value ==original_txt:
                return True
    return False

@register.filter(name='alter_txt')
def alter_txt(value, mapping):
    """ Use as txt -- Alternative text for original text """
    value = str(value)
    alternative_txt = ""
    if mapping:
        for dict in mapping:
            original_txt = dict.get("original_txt")
            if(value == original_txt):
                alternative_txt = dict.get("alternative_txt")
                return alternative_txt
    # if not use as text return empty
    return ""

@register.filter(name='alter_txt_default')
def alter_txt_default(value, mapping):
    """
    Use as txt -- Alternative text for original text
    if alternate not found return original text i.e. default
    """
    value = str(value)
    alternative_txt = ""
    if mapping:
        for dict in mapping:
            original_txt = dict.get("original_txt")
            if(value == original_txt):
                alternative_txt = dict.get("alternative_txt")
                return alternative_txt
    # if not use as text return empty
    return value


@register.filter(name='alter_comma_separated')
def alter_comma_separated(value, mapping):
    """
    Use as txt --
        * split string by comma
        * loop in values
        * get alternative text of value
        * store into new list
        * finally join list into string back
    """
    if value:
        value = str(value)
        alternative_txt_list = []

        list_splitted_words = [x.strip() for x in value.split(',')]

        if mapping:
            for word in list_splitted_words:
                flag_is_alternate_found = False
                for dict in mapping:
                    original_txt = dict.get("original_txt")
                    if word == original_txt:
                        alternative_txt = dict.get("alternative_txt")
                        flag_is_alternate_found = True
                        alternative_txt_list.append(alternative_txt)
                if not flag_is_alternate_found:
                    # if alternate not found keep original
                    alternative_txt_list.append(word)

        if alternative_txt_list:
            s = ", ";
            return s.join(alternative_txt_list)  # a, b, c # comma and space
        else:
            # if not use as text return empty
            return value
    else:
        return "None"


@register.filter(name='get_volume')
def get_volume(value, volume_and_cpls):
    """ Use as txt -- Alternative text for original text """
    value = str(value)
    volume = ""
    if volume_and_cpls:
        for dict in volume_and_cpls:
            level_of_intent = dict.get("level_of_intent")
            if(value == level_of_intent):
                volume = dict.get("volume")
                return volume
    # if not use as text return empty
    return ""

@register.filter(name='get_cpl')
def get_cpl(value, volume_and_cpls):
    """ get cpl from volume and cpl list of dicts"""
    value = str(value)
    cpl = ""
    if volume_and_cpls:
        for dict in volume_and_cpls:
            level_of_intent = dict.get("level_of_intent")
            if(value == level_of_intent):
                cpl = dict.get("cpl")
                return cpl
    # if not use as text return empty
    return ""


@register.filter()
def to_int(value):
    return int(value)


########################################
# incrementing variable in template
########################################
'''
usage
{% ++ <var_name> %}
For example
{% ++ a %}
'''
def increment_var(parser, token):

    parts = token.split_contents()
    if len(parts) < 2:
        raise template.TemplateSyntaxError("'increment' tag must be of the form:  {% increment <var_name> %}")
    return IncrementVarNode(parts[1])

register.tag('++', increment_var)

class IncrementVarNode(template.Node):

    def __init__(self, var_name):
        self.var_name = var_name

    def render(self,context):
        try:
            value = context[self.var_name]
            context[self.var_name] = value + 1
            return u""
        except:
            raise template.TemplateSyntaxError("The variable does not exist.")



@register.filter(name='ifin_strlist')
def ifin_strlist(value, str_list):
    if value != None and str_list != None:
        str_list = str_list.lower()
        value = str(value).lower()
        # print(value)
        # print(str_list)
        return True if value in str_list.split(",") else False
    else:
        return False


@register.filter(name='adding')
def adding(value, args):
    return value+args


@register.filter(name='modifying')
def modifying(value):
    import dateutil.parser
    return dateutil.parser.parse(value)
